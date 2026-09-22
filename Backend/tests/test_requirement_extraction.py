"""Tests for structured requirement extraction (Phase 3)."""
from app.services.extractor import (
    PageText, RuleBasedRequirementExtractor, build_product_vocabulary, extract_pdf_pages,
)

STANDARDS = [
    {"is_number": "TEST-IS-CEMENT", "product": "Cement", "sector": "Building Materials", "keywords": ["opc", "binder"]},
    {"is_number": "TEST-IS-LAMP", "product": "LED Lamp", "sector": "Electrical", "keywords": ["led", "binder"]},
]


def _extract(text, page=1, vocab=None):
    return RuleBasedRequirementExtractor(vocab).extract([PageText(page, text)])


def test_numbered_clauses_split_and_wrapped_lines_joined():
    reqs = _extract("4.1 The cement shall be\nOrdinary Portland Cement.\n4.2 It shall conform to IS 269:2015.")
    assert [r.raw_text for r in reqs] == [
        "4.1 The cement shall be Ordinary Portland Cement.",
        "4.2 It shall conform to IS 269:2015.",
    ]
    assert [r.requirement_id for r in reqs] == ["REQ-001", "REQ-002"]
    assert reqs[1].parameters["clause_ref"] == "4.2"


def test_raw_text_is_verbatim_apart_from_whitespace():
    original = "The pipe shall have  a wall thickness of 3.2   mm."
    assert _extract(original)[0].raw_text == " ".join(original.split())


def test_page_numbers_preserved_across_pages():
    reqs = RuleBasedRequirementExtractor().extract([
        PageText(1, "1. Cement shall conform to IS 269."),
        PageText(2, "2. Pipe wall thickness shall be 3.2 mm."),
    ])
    assert [r.source_page for r in reqs] == [1, 2]


def test_cited_standards_recorded_as_written_not_verified():
    r = _extract("The lamp shall comply with IS 302 (Part 1) : 2024 and IS/IEC 60335-1.")[0]
    assert r.parameters["cited_standards"] == ["IS 302 (Part 1) : 2024", "IS/IEC 60335-1"]


def test_measurements_and_grade_extracted():
    r = _extract("Cement of 43 grade shall be supplied in 50 kg bags with 12 mm cover at 230 V.")[0]
    units = {m["unit"] for m in r.parameters["measurements"]}
    assert {"kg", "mm", "v"} <= units
    assert r.parameters["grade"] == ["43"]


def test_mandatory_detection_true_false_none_and_conflict():
    assert _extract("The cement shall be OPC.")[0].mandatory is True
    assert _extract("Fire retardant coating is optional for the cement.")[0].mandatory is False
    assert _extract("Cement should be stored in dry conditions per specification.")[0].mandatory is None
    assert _extract("Cement shall be OPC and packaging may be jute or plastic.")[0].mandatory is None


def test_product_and_category_only_from_vocabulary():
    vocab = build_product_vocabulary(STANDARDS)
    r = _extract("Supply of OPC cement shall be as per specification.", vocab=vocab)[0]
    assert r.product == "Cement" and r.category == "Building Materials"
    assert _extract("The pump shall be tested at site.", vocab=vocab)[0].product is None
    assert _extract("Cement shall be OPC 43 grade.")[0].product is None  # no vocabulary => not guessed


def test_vocabulary_drops_ambiguous_alias():
    vocab = build_product_vocabulary(STANDARDS)
    assert "binder" not in vocab and "opc" in vocab and vocab["led lamp"] == ("LED Lamp", "Electrical")


def test_multiple_products_extracted_separately():
    vocab = build_product_vocabulary(STANDARDS)
    reqs = _extract("Cement and LED lamp shall conform to specification.", vocab=vocab)
    assert len(reqs) == 2
    assert reqs[0].product == "Cement"
    assert reqs[1].product == "LED Lamp"


def test_administrative_clauses_are_excluded():
    text = "1. The bidder shall submit earnest money before the deadline.\n2. Cement shall conform to IS 269."
    reqs = _extract(text)
    assert len(reqs) == 1 and "IS 269" in reqs[0].raw_text


def test_short_headings_and_page_furniture_ignored():
    assert [r.raw_text for r in _extract("TECHNICAL SPECIFICATIONS\n\nPage 3\n\n1. Cement shall conform to IS 269.")] == [
        "1. Cement shall conform to IS 269."
    ]


def test_short_freetext_falls_back_to_single_requirement():
    reqs = _extract("high strength building powder for foundations")
    assert len(reqs) == 1 and reqs[0].raw_text == "high strength building powder for foundations"
    assert reqs[0].mandatory is None and reqs[0].source_page == 1


def test_long_text_with_no_requirements_returns_empty():
    assert _extract("Lorem ipsum dolor sit amet consectetur. " * 30) == []


def test_unnumbered_paragraph_split_into_sentences():
    reqs = _extract("Cement shall be OPC. It shall conform to IS 269. The pipe shall be 3 mm thick.")
    assert len(reqs) == 3


def test_empty_pages_yield_nothing():
    assert RuleBasedRequirementExtractor().extract([PageText(1, "")]) == []


def test_pdf_to_requirements_end_to_end(make_pdf):
    pdf = make_pdf([
        "TECHNICAL SPECIFICATIONS\n4.1 Cement shall conform to IS 269:2015.",
        "5.1 Steel pipe wall thickness shall be 3.2 mm.\n6.1 The bidder shall submit EMD.",
    ])
    reqs = RuleBasedRequirementExtractor().extract(extract_pdf_pages(pdf))
    assert [(r.source_page, r.parameters["clause_ref"]) for r in reqs] == [(1, "4.1"), (2, "5.1")]


def test_is_reference_year_vs_part_suffix_not_confused():
    r = _extract("Cement shall conform to IS 269-2015 and IS 302-1 as specified.")[0]
    assert r.parameters["cited_standards"] == ["IS 269-2015", "IS 302-1"]
