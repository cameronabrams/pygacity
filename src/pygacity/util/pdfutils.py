# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""
PDF utility functions for pygacity
"""
import PyPDF2

def combine_pdfs(args):
    pdf_list = args.i
    output_filename = args.o
    merger = PyPDF2.PdfMerger()

    for pdf in pdf_list:
        merger.append(pdf)

    merger.write(output_filename)
    merger.close()
    print(f"Combined PDF saved as: {output_filename}")

def duplicate_last_page(input_pdf, output_pdf):
    """
    Duplicate the last page of a PDF document and append it to the end.

    Args:
        input_pdf: Path to the input PDF file
        output_pdf: Path to save the modified PDF file
    """
    reader = PyPDF2.PdfReader(input_pdf)
    writer = PyPDF2.PdfWriter()

    # Add all existing pages
    for page in reader.pages:
        writer.add_page(page)

    # Duplicate and append the last page
    if len(reader.pages) > 0:
        last_page = reader.pages[-1]
        writer.add_page(last_page)

    # Write to output file
    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)

    print(f"Duplicated last page and saved as: {output_pdf}")
