from app.core.constants import DocumentType
from app.services.parsing.classifier import DocumentClassifier


def test_classify_affidavit():
    text = "I, Deponent solemnly affirm and state on oath that I have good moral character."
    doc_type, confidence = DocumentClassifier.classify(text)
    assert doc_type == DocumentType.AFFIDAVIT_OF_CHARACTER
    assert confidence > 0.3


def test_classify_rent_agreement():
    text = "This rent agreement is made between Landlord and Tenant for demised premises at monthly rent of 25,000."
    doc_type, confidence = DocumentClassifier.classify(text)
    assert doc_type == DocumentType.RENT_AGREEMENT
    assert confidence > 0.3


def test_classify_legal_notice():
    text = "Under instructions from my client, I hereby call upon you to pay the sum within 15 days failing which."
    doc_type, confidence = DocumentClassifier.classify(text)
    assert doc_type == DocumentType.LEGAL_NOTICE
    assert confidence > 0.3