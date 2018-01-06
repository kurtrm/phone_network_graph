"""
Test parser to ensure we are getting expected values.

Many tests target assumptions, not necessarily code.
"""
import os
import pickle
import pytest
import PyPDF2

from src import tmobile_bill_parser as parser

"""

These fixtures maintained for posterity. Pickling reduced test times
significantly. Maintain for extracting bill text if something happens
to the pickle.


@pytest.fixture
def pdf_docs_function(pdf_docs):
    Fixture that extracts text from the pdf.
    paths = ['../bills/' + bill for bill in os.listdir('../bills')]
    bills = []
    for bill in paths:
        page_texts = []
        pdf_bill = PyPDF2.PdfFileReader(open(bill, 'rb'))
        for page in range(3, pdf_bill.numPages):
            raw_page = pdf_bill.getPage(page)
            raw_text = raw_page.extractText()
            prepared_page = raw_text.split('\n')
            page_texts.append(prepared_page)
        bills.append(page_texts)
    return bills
"""


@pytest.fixture
def pdf_docs():
    """Fixture containing all bills."""
    paths = ['bills/' + bill for bill in os.listdir('bills/')]
    return paths


@pytest.fixture
def pdf_docs_text():
    """Fixturize the pickle of the pdf texts."""
    bills = pickle.load(open('tests/text_docs.p', 'rb'))
    return bills


def test_third_page_as_start_assumption(pdf_docs):
    """Test that the starting page contains unique text."""
    for bill in pdf_docs:
        pdf_bill = PyPDF2.PdfFileReader(open(bill, 'rb'))
        page = pdf_bill.getPage(3)
        page = page.extractText()
        assert 'Usage details' in page


def test_second_page_not_starting_point(pdf_docs):
    """Test page before starting page does not contain starting text."""
    for bill in pdf_docs:
        pdf_bill = PyPDF2.PdfFileReader(open(bill, 'rb'))
        page = pdf_bill.getPage(2)
        page = page.extractText()
        assert 'Usage details' not in page


def test_fourth_page_not_starting_point(pdf_docs):
    """Test that the next page never contains 'Usage details'."""
    for bill in pdf_docs:
        pdf_bill = PyPDF2.PdfFileReader(open(bill, 'rb'))
        page = pdf_bill.getPage(2)
        page = page.extractText()
        assert 'Usage details' not in page


def test_last_character_assumption_after_split(pdf_docs_text):
    """Test that the last character is an empty string after splitting."""
    for bill in pdf_docs_text:
        for text in bill:
            assert text[-1] == ''


def test_all_data_gathered_continuous(pdf_docs_text):
    """
    Ensure we're getting all the data from continuous records.

    We subtract 6 from the len in the assert to account for the column headers.
    """
    for bill in pdf_docs_text:
        for text in bill:
            if 'Total' not in text:
                datetime = text.index('Date and time')
                sect = parser._parse_continuous_records(text[datetime:], {})
                assert len(text[datetime:]) - 6 == sum(len(sect[key])
                                                       for key in sect.keys())


def test_discontinuous_section_label_assumption(pdf_docs_text):
    """Ensure section label is constant on discontinuous records."""
    for bill in pdf_docs_text:
        for text in bill:
            if 'Total:' in text:
                date_time = text.index('Date and time')
                assert text[date_time - 2] in ['Text', 'Talk', 'Data']


def test_discontinuous_next_section_assumption(pdf_docs_text):
    """Ensure section label is constant on discontinuous records."""
    for bill in pdf_docs_text:
        for text in bill:
            try:
                end = text.index('Total:')
            except ValueError:
                continue
            try:
                assert text[end + 4] == 'Date and time'
            except IndexError:
                continue
            except AssertionError:
                assert text[end + 5] == 'Date and time'


def test_single_parser_error():
    """Ensure value error raised in both functions."""
    with pytest.raises(ValueError):
        parser.parse_bill('/billybills')


def test_multiple_parser_error():
    """Ensure value error arised in this function too."""
    with pytest.raises(ValueError):
        parser.parse_multiple_bills('/filename')
