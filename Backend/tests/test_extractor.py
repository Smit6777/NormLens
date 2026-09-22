"""Tests for document text extraction (Phase 3): PDF, plain text, upload validation."""
import pytest

from app.core.exceptions import DocumentExtractionError, FileTooLargeError, UnsupportedFileTypeError
from app.services.extractor import (
    extract_document, extract_pdf_pages, extract_text_pages, validate_upload,
)

ALLOWED = [".pdf", ".txt"]


def test_pdf_pages_and_numbers_preserved(make_pdf):
    pages = extract_pdf_pages(make_pdf(["Page one text about cement", "Page two text about lamps", "Third page"]))
    assert [p.page_number for p in pages] == [1, 2, 3]
    assert "cement" in pages[0].text and "lamps" in pages[1].text and "Third" in pages[2].text


def test_pdf_multiline_and_special_chars(make_pdf):
    pages = extract_pdf_pages(make_pdf(["4.2 Cement shall conform to IS 269 (2015)\nsecond line"]))
    assert "IS 269 (2015)" in pages[0].text and "second line" in pages[0].text.splitlines()[1]


def test_pdf_with_blank_page_keeps_page_numbering(make_pdf):
    pages = extract_pdf_pages(make_pdf(["First page has text", "", "Third page has text"]))
    assert len(pages) == 3 and pages[1].text.strip() == "" and pages[2].page_number == 3


def test_pdf_with_no_text_is_rejected_as_needing_ocr(make_pdf):
    with pytest.raises(DocumentExtractionError, match="OCR"):
        extract_pdf_pages(make_pdf(["", ""]))


def test_corrupt_pdf_rejected():
    with pytest.raises(DocumentExtractionError):
        extract_pdf_pages(b"%PDF-1.4\nthis is not really a pdf at all")


def test_non_pdf_bytes_rejected():
    with pytest.raises(DocumentExtractionError, match="not a valid PDF"):
        extract_pdf_pages(b"MZ\x90\x00 executable pretending to be pdf")


def test_plain_text_single_page_without_number():
    pages = extract_text_pages("Supply of cement shall conform to IS 269.")
    assert len(pages) == 1 and pages[0].page_number is None


def test_text_bytes_utf8_bom_and_cp1252_fallback():
    assert extract_text_pages("\ufeffhello world".encode("utf-8"))[0].text == "hello world"
    assert "caf\u00e9" in extract_text_pages("caf\u00e9 lamp".encode("cp1252"))[0].text


def test_empty_text_rejected():
    with pytest.raises(DocumentExtractionError):
        extract_text_pages("   \n ")


def test_validate_upload_extension_and_size():
    assert validate_upload("Tender.PDF", 10, ALLOWED, 100) == ".pdf"
    with pytest.raises(UnsupportedFileTypeError):
        validate_upload("malware.exe", 10, ALLOWED, 100)
    with pytest.raises(UnsupportedFileTypeError):
        validate_upload("noextension", 10, ALLOWED, 100)
    with pytest.raises(FileTooLargeError):
        validate_upload("a.pdf", 101, ALLOWED, 100)


def test_extract_document_pdf_reports_page_count_and_basename(make_pdf):
    doc = extract_document("../../etc/tender.pdf", make_pdf(["one page of text here"]), ALLOWED, 10**6)
    assert doc.filename == "tender.pdf" and doc.page_count == 1


def test_extract_document_txt_has_no_page_count():
    doc = extract_document("spec.txt", b"Cement shall be OPC 43 grade.", ALLOWED, 10**6)
    assert doc.page_count is None and doc.pages[0].page_number is None


def test_extract_document_pdf_extension_with_fake_content_rejected():
    with pytest.raises(DocumentExtractionError):
        extract_document("fake.pdf", b"plain text pretending to be pdf", ALLOWED, 10**6)
