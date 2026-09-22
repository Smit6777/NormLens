"""
Document text extraction and structured requirement extraction.

Two separable layers:
  1. Text extraction (PDF via pdfplumber, or plain text) -> `PageText` list,
     with page numbers preserved.
  2. Requirement extraction: `RequirementExtractor` is a small Protocol.
     `RuleBasedRequirementExtractor` is the MVP implementation; an
     LLM-based extractor can replace it later without changing the
     `ExtractedRequirement` API contract.

Rules honoured here:
  * Rule 4 -- `raw_text` is the tender's own wording. The only change
    made is collapsing line-wrap whitespace into single spaces.
  * Rule 1/2 -- nothing is guessed. `product`/`category` come only from a
    vocabulary derived from the knowledge base; `mandatory` is None when
    the wording is absent or conflicting. Standards "cited" in a tender
    are recorded exactly as written and are NOT verified here.

PDFs are read from memory (no temp files are written). pdfplumber is
synchronous and CPU-bound: the API layer (Phase 6) must call these
functions from a threadpool.
"""
from __future__ import annotations

import io
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Protocol

from app.core.exceptions import DocumentExtractionError, FileTooLargeError, UnsupportedFileTypeError
from app.core.logging import get_logger
from app.models.schemas import ExtractedRequirement

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PageText:
    """Text of one page. `page_number` is 1-based, or None for plain-text input."""

    page_number: int | None
    text: str


@dataclass(frozen=True)
class ExtractedDocument:
    filename: str | None
    pages: list[PageText]

    @property
    def page_count(self) -> int | None:
        return len(self.pages) if self.pages and self.pages[0].page_number is not None else None


def validate_upload(filename: str, size_bytes: int, allowed_extensions: Iterable[str], max_bytes: int) -> str:
    """Validate an upload's name and size. Returns the lower-cased extension (e.g. '.pdf')."""
    ext = Path(filename or "").suffix.lower()
    allowed = [e.lower() for e in allowed_extensions]
    if ext not in allowed:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{ext or 'none'}'. Allowed: {', '.join(allowed)}.",
            details={"extension": ext, "allowed": allowed},
        )
    if size_bytes > max_bytes:
        raise FileTooLargeError(
            f"File is {size_bytes} bytes; the limit is {max_bytes} bytes.",
            details={"size_bytes": size_bytes, "max_bytes": max_bytes},
        )
    return ext


def extract_pdf_pages(data: bytes) -> list[PageText]:
    """Extract text per page from PDF bytes. Scanned/image-only PDFs are rejected (no OCR in the MVP)."""
    if not data.lstrip()[:5] == b"%PDF-":
        raise DocumentExtractionError("File content is not a valid PDF.")
    import pdfplumber  # lazy: keeps this module importable without pdfplumber

    pages: list[PageText] = []
    try:
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for number, page in enumerate(pdf.pages, start=1):
                pages.append(PageText(page_number=number, text=page.extract_text() or ""))
    except DocumentExtractionError:
        raise
    except Exception as exc:  # pdfminer raises many types for corrupt/encrypted files
        logger.exception("PDF extraction failed")
        raise DocumentExtractionError(
            "Could not read the PDF (it may be corrupt or password-protected).",
            details={"reason": type(exc).__name__},
        ) from exc

    if not any(p.text.strip() for p in pages):
        raise DocumentExtractionError(
            "No extractable text found. Scanned/image-only PDFs need OCR, which the MVP does not support; "
            "paste the text instead.",
            details={"page_count": len(pages)},
        )
    return pages


def extract_text_pages(content: bytes | str) -> list[PageText]:
    """Wrap plain text as a single page with no page number."""
    if isinstance(content, bytes):
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            try:
                text = content.decode("cp1252")
                logger.warning("Text file was not UTF-8; decoded as cp1252.")
            except UnicodeDecodeError as exc:
                raise DocumentExtractionError("Could not decode the text file (expected UTF-8).") from exc
    else:
        text = content
    if not text.strip():
        raise DocumentExtractionError("The text input is empty.")
    return [PageText(page_number=None, text=text)]


def extract_document(
    filename: str, content: bytes, allowed_extensions: Iterable[str], max_bytes: int
) -> ExtractedDocument:
    """Validate an upload then extract its text. Only the basename is kept; nothing is written to disk."""
    ext = validate_upload(filename, len(content), allowed_extensions, max_bytes)
    basename = Path(filename).name
    # Security: sanitize filename
    import re
    sanitized = re.sub(r'[^a-zA-Z0-9.\-_]', '_', basename)
    pages = extract_pdf_pages(content) if ext == ".pdf" else extract_text_pages(content)
    return ExtractedDocument(filename=sanitized, pages=pages)


# ---------------------------------------------------------------------------
# Requirement extraction
# ---------------------------------------------------------------------------

ProductVocabulary = dict[str, tuple[str, str | None]]  # lower-case term -> (canonical product, sector)


class RequirementExtractor(Protocol):
    """Anything that turns pages into structured requirements (rule-based now, LLM later)."""

    def extract(self, pages: list[PageText]) -> list[ExtractedRequirement]: ...


def build_product_vocabulary(standards: Iterable[dict[str, Any]]) -> ProductVocabulary:
    """Derive a product vocabulary from knowledge-base records (never invented).

    Product names map to themselves; a keyword becomes an alias only if it
    points at exactly one product (ambiguous aliases are dropped).
    """
    sectors: dict[str, set[str | None]] = {}
    canonical: dict[str, str] = {}
    alias_targets: dict[str, set[str]] = {}
    for rec in standards:
        product = (rec.get("product") or "").strip()
        if not product:
            continue
        key = product.lower()
        canonical[key] = product
        sectors.setdefault(key, set()).add((rec.get("sector") or None))
        for kw in rec.get("keywords") or []:
            kw_key = str(kw).strip().lower()
            if kw_key:
                alias_targets.setdefault(kw_key, set()).add(key)

    def sector_of(key: str) -> str | None:
        found = {s for s in sectors[key] if s}
        return next(iter(found)) if len(found) == 1 else None

    vocab: ProductVocabulary = {key: (canonical[key], sector_of(key)) for key in canonical}
    for alias, targets in alias_targets.items():
        if alias not in vocab and len(targets) == 1:
            target = next(iter(targets))
            vocab[alias] = (canonical[target], sector_of(target))
    return vocab


_IS_REF_RE = re.compile(
    r"\bIS(?:/(?:ISO|IEC))?\s*[:\-]?\s*\d{1,6}(?:-\d{1,3}(?!\d))?(?:\s*\(\s*Part\s*\d+[A-Za-z]?\s*\))?(?:\s*[:\-]\s*\d{4})?"
)
_MEASURE_RE = re.compile(
    r"(?<![\w.])(\d+(?:\.\d+)?)\s*"
    r"(mm2|mm²|m2|m²|m3|m³|mm|cm|km|kg|mg|mpa|gpa|kn|n/mm2|n/mm²|kv|khz|hz|ma|ml|lm|litres?|liters?|°c|[mgvwl])"
    r"(?![\w²³])|(?<![\w.])(\d+(?:\.\d+)?)\s*(%)",
    re.IGNORECASE,
)
_GRADE_RE = re.compile(r"\b(\d{1,3})\s*grade\b|\bgrade\s*[:\-]?\s*([A-Za-z]?\d{1,3}[A-Za-z]?)\b", re.IGNORECASE)
_MANDATORY_RE = re.compile(r"\b(shall|must|mandatory|mandatorily|compulsory|required)\b", re.IGNORECASE)
_OPTIONAL_RE = re.compile(r"\b(optional|may|desirable|preferably)\b", re.IGNORECASE)
_MODAL_RE = re.compile(r"\b(shall|must|should|mandatory|compulsory|required)\b", re.IGNORECASE)
_TECH_CUE_RE = re.compile(
    r"\b(conform(?:s|ing)?|compl(?:y|ies|ying)|specification|specified|standard|tested|testing|test|"
    r"certified|certification|bis|isi|quality|material|grade)\b",
    re.IGNORECASE,
)
_ADMIN_CUE_RE = re.compile(
    r"\b(bidder|tenderer|emd|earnest money|payment|invoice|penalt\w*|submit|submission|deadline|"
    r"validity|arbitration|jurisdiction|gst|bank guarantee|eligib\w+|turnover)\b",
    re.IGNORECASE,
)
_HEADING_RE = re.compile(
    r"^(?:TENDER FOR|NOTICE INVITING|TECHNICAL SPECIFICATION|SCOPE OF WORK|TERMS AND CONDITIONS|DELIVERY PERIOD|GENERAL CONDITIONS|ANNEXURE|SECTION)\b",
    re.IGNORECASE
)
_CLAUSE_START_RE = re.compile(r"^\s*(?:(\d+(?:\.\d+)*)[.)]?|\(([a-zA-Z0-9]{1,3})\)|[a-zA-Z][.)]|[-•*])\s+")
_CLAUSE_REF_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)[.)]?\s+")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.;])\s+(?=[A-Z(])")

_MIN_WORDS = 3
_FALLBACK_MAX_CHARS = 500


class RuleBasedRequirementExtractor:
    """Heuristic clause extractor. Deterministic, dependency-free, replaceable."""

    def __init__(self, vocabulary: ProductVocabulary | None = None) -> None:
        self._vocab = vocabulary or {}
        self._vocab_re = None
        if self._vocab:
            terms = sorted(self._vocab, key=len, reverse=True)
            self._vocab_re = re.compile(
                r"(?<!\w)(" + "|".join(re.escape(t) for t in terms) + r")(?!\w)", re.IGNORECASE
            )

    # -- public ---------------------------------------------------------

    def extract(self, pages: list[PageText]) -> list[ExtractedRequirement]:
        clauses: list[tuple[int | None, str]] = []
        for page in pages:
            clauses.extend((page.page_number, c) for c in self._split_clauses(page.text))

        requirements: list[ExtractedRequirement] = []
        for page_number, clause in clauses:
            info = self._analyze(clause)
            if info is None:
                continue
            requirements.append(
                ExtractedRequirement(
                    requirement_id=f"REQ-{len(requirements) + 1:03d}",
                    raw_text=clause,
                    product=info["product"],
                    category=info["category"],
                    parameters=info["parameters"],
                    mandatory=info["mandatory"],
                    source_page=page_number,
                )
            )

        if not requirements:
            whole = " ".join(word for p in pages for word in p.text.split())
            if _MIN_WORDS <= len(whole.split()) and len(whole) <= _FALLBACK_MAX_CHARS:
                # Short free-text input (e.g. a one-line query): treat it as one requirement.
                info = self._analyze(whole, force=True)
                requirements.append(
                    ExtractedRequirement(
                        requirement_id="REQ-001", raw_text=whole, product=info["product"],
                        category=info["category"], parameters=info["parameters"],
                        mandatory=info["mandatory"], source_page=pages[0].page_number if pages else None,
                    )
                )
        logger.info("Requirements extracted", extra={"context": {"count": len(requirements)}})
        return requirements

    # -- internals ------------------------------------------------------

    @staticmethod
    def _split_clauses(text: str) -> list[str]:
        clauses: list[str] = []
        for block in re.split(r"\n\s*\n", text):
            lines = [ln for ln in block.splitlines() if ln.strip()]
            if not lines:
                continue
            groups: list[list[str]] = []
            for line in lines:
                if _CLAUSE_START_RE.match(line) or not groups:
                    groups.append([line.strip()])
                else:
                    groups[-1].append(line.strip())
            numbered = any(_CLAUSE_START_RE.match(ln) for ln in lines)
            for group in groups:
                joined = " ".join(" ".join(group).split())
                if numbered or len(groups) > 1:
                    clauses.append(joined)
                else:
                    clauses.extend(s.strip() for s in _SENTENCE_SPLIT_RE.split(joined) if s.strip())
        return clauses


    def _analyze(self, clause: str, force: bool = False) -> dict[str, Any] | None:
        if _HEADING_RE.match(clause.strip()):
            return None

        if not force and len(clause.split()) < _MIN_WORDS:
            return None

        cited = [" ".join(m.group(0).split()) for m in _IS_REF_RE.finditer(clause)]
        measurements = [
            {"value": m.group(1) or m.group(3), "unit": (m.group(2) or m.group(4)).lower(), "text": m.group(0).strip()}
            for m in _MEASURE_RE.finditer(clause)
        ]
        grades = [g1 or g2 for g1, g2 in _GRADE_RE.findall(clause)]

        products: list[str] = []
        category: str | None = None
        if self._vocab_re is not None:
            for m in self._vocab_re.finditer(clause):
                canon, sector = self._vocab[m.group(1).lower()]
                if canon not in products:
                    products.append(canon)
                    if len(products) == 1:
                        category = sector

        technical = bool(cited or measurements or grades or products or _TECH_CUE_RE.search(clause))
        modal = bool(_MODAL_RE.search(clause))
        if not force and not (technical or (modal and not _ADMIN_CUE_RE.search(clause))):
            return None

        parameters: dict[str, Any] = {}
        ref = _CLAUSE_REF_RE.match(clause)
        if ref:
            parameters["clause_ref"] = ref.group(1)
        if cited:
            parameters["cited_standards"] = cited  # as written in the tender; NOT verified
        if measurements:
            parameters["measurements"] = measurements
        if grades:
            parameters["grade"] = grades
        if len(products) > 1:
            parameters["products_mentioned"] = products

        has_mand, has_opt = bool(_MANDATORY_RE.search(clause)), bool(_OPTIONAL_RE.search(clause))
        mandatory = True if has_mand and not has_opt else False if has_opt and not has_mand else None

        return {
            "product": products[0] if products else None,
            "category": category,
            "parameters": parameters,
            "mandatory": mandatory,
        }
