"""Module for parsing tmobile bill PDFs.

After removing line feeds and empty strings, the resulting text
has a fairly consistent pattern with some minor nuances.

The data we want to collect starts on page 4 (index 3) of the bill.
parsing_start = 3

On each page thereafter, 'Date and time' marks the beginning of the
column headers and the data. There are 6 columns per section, thus:
columns = 6

Sections will end, and new sections will start on the same page. 'Total:'
is consistently the marker for the end of each section. Worth noting,
the text two indeces ahead of this marker is the title of the next section,
which we check to see if it's the last section 'Data'. (end + 2)
TODO: Verify logic is correct for the while loop in _parse_discontinous.

We also grab the text two indeces behind 'Date and time' in order to use
it as the key for the master bill_dict the function will return. (start - 2)

Lastly, there's a difference in the spacing between the start of the next
section in the transition between 'Text' and 'Data', thus the check to see
if the section is 'Data' in _parse_discontinuous_records.
end + 4 or end + 5

"""
import os
import PyPDF2


def parse_bill(filename):
    """House the main logic for determining when to use which functions.

    Based on markers on each PDF page.
    """
    if not os.path.isfile(filename):
        raise ValueError("Not a valid file path.")
    pdf_bill = PyPDF2.PdfFileReader(open(filename, 'rb'))
    bill_dict = {}
    section_dict = {}
    bill_list = []
    parsing_start = 3 if filename not in ['../bills/Mom_and_Dad/sep17-oct17.pdf',
                                          '../bills/Mom_and_Dad/may17-jun17.pdf',
                                          '../bills/Mom_and_Dad/mar17-apr17.pdf',
                                          '../bills/Mom_and_Dad/jun17-jul17.pdf',
                                          '../bills/Mom_and_Dad/jul17-aug17.pdf',
                                          '../bills/Mom_and_Dad/feb17-mar17.pdf',
                                          '../bills/Mom_and_Dad/aug17-sep17.pdf',
                                          '../bills/Mom_and_Dad/apr17-may17.pdf'] else 4

    for page in range(parsing_start, pdf_bill.numPages):
        prepared_page = _prepare_bill(pdf_bill, page)
        if 'Total:' in prepared_page:
            (bill_dict,
             section_dict) = _parse_discontinuous_records(prepared_page,
                                                          bill_dict,
                                                          section_dict)
            if prepared_page[34] == 'Data' and 'Total:' in prepared_page:
                bill_list.append(bill_dict.copy())
                bill_dict = {}
        else:
            section_dict = _parse_continuous_records(prepared_page,
                                                     section_dict)
    return bill_list


def parse_multiple_bills(directory):
    """Take a list of filenames or a directory and return several bills."""
    if not os.path.isdir(directory):
        raise ValueError("Not a valid file path.")
    bill_list = os.listdir(directory)
    bill_directory = {}
    for bill in bill_list:
        path = directory + bill
        bill_key = bill[:-4]
        bill_directory[bill_key] = parse_bill(path)

    return bill_directory


def _prepare_bill(pdf, page):
    """Prepare the PDF page to be parsed.

    Due to the nature of the document, we need to preserve some whitesapce,
    thus we split on returns and remove the last item in the list which is
    an empty string.
    """
    raw_page = pdf.getPage(page)
    raw_text = raw_page.extractText()
    prepared_page = raw_text.split('\n')[:-1]

    return prepared_page


def _parse_discontinuous_records(prepared_page, bill_dict, section_dict):
    """Handle parsing a page that has a break in the pattern of records.

    For example, the 'Talk' section ends and the 'Text' section begins.
    """
    columns = 6
    start = prepared_page.index('Date and time')
    end = prepared_page.index('Total:')
    while True:
        tail_dict = {}
        section_label = prepared_page[start - 2]
        for i, column in enumerate(prepared_page[start:start + columns]):
            column_index = start + i
            tail_dict[column] = prepared_page[column_index + columns:end:columns]
        bill_dict[section_label] = {key: section_dict.get(key, []) + tail_dict[key]
                                    for key in tail_dict.keys()}
        if end + 2 < len(prepared_page) and prepared_page[end + 2] == 'Data':
            start_section = end + 4
        elif end + 4 < len(prepared_page) and prepared_page[end + 4] == 'Talk':
            start_section = end + 6
        else:
            start_section = end + 5
        if 'Total:' in prepared_page[start_section:]:
            start = start_section
            end = prepared_page.index('Total:', start_section)
            section_dict = {}
            # import pdb; pdb.set_trace()
            continue
        next_section = prepared_page[start_section:]
        section_dict = {}
        for column in next_section[:columns]:
            column_index = next_section.index(column)
            section_dict[column] = next_section[column_index + columns::columns]

        return bill_dict, section_dict


def _parse_continuous_records(prepared_page, section_dict):
    """Handle parsing a continuous list of records."""
    # import pdb; pdb.set_trace()
    columns = 6
    start = prepared_page.index('Date and time')
    for i, column in enumerate(prepared_page[start:start + columns]):
        column_index = start + i
        values = prepared_page[column_index + columns::columns]
        if column in section_dict:
            section_dict[column] = section_dict[column] + values
        else:
            section_dict[column] = values

    return section_dict
