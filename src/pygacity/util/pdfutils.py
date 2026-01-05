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
