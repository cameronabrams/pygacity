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

def bundle_pdfs(pdf_paths: list, output_path, two_sided: bool = False):
    """
    Merge a list of PDF files into a single bundle PDF.

    Parameters
    ----------
    pdf_paths : list of str or Path
        Ordered list of PDF files to include in the bundle.
    output_path : str or Path
        Destination path for the merged bundle PDF.
    two_sided : bool, optional
        If True, pad each exam to an even page count by appending a blank page
        when the exam has an odd number of pages.  This ensures the first page
        of every exam falls on a right-hand (odd) sheet side when printed
        double-sided (default: False).
    """
    writer = PyPDF2.PdfWriter()
    for pdf in pdf_paths:
        reader = PyPDF2.PdfReader(str(pdf))
        for page in reader.pages:
            writer.add_page(page)
        if two_sided and len(reader.pages) % 2 != 0:
            last = reader.pages[-1]
            writer.add_blank_page(
                width=last.mediabox.width,
                height=last.mediabox.height,
            )
    with open(output_path, 'wb') as fh:
        writer.write(fh)


def bundle_subcommand(args):
    """
    CLI subcommand: bundle student exam PDFs found in a build directory.

    Student PDFs are identified by excluding files whose names contain
    ``_soln``, ``answerset``, or ``bundle``.  They are sorted by
    modification time (build order) before being chunked.
    """
    from pathlib import Path
    build_dir = Path(args.build_dir)
    if not build_dir.is_dir():
        raise NotADirectoryError(f'"{build_dir}" is not a directory')

    all_pdfs = sorted(build_dir.glob('*.pdf'), key=lambda p: p.stat().st_mtime)
    student_pdfs = [
        p for p in all_pdfs
        if not any(tag in p.stem for tag in ('_soln', 'answerset', 'bundle'))
    ]
    if not student_pdfs:
        print(f'No student exam PDFs found in {build_dir}')
        return

    # Derive a job name from the common stem prefix (everything before the last '-')
    job_name = student_pdfs[0].stem.rsplit('-', 1)[0] if '-' in student_pdfs[0].stem else student_pdfs[0].stem

    bundle_size = args.bundle_size
    two_sided = args.two_sided
    chunks = [student_pdfs[i:i + bundle_size] for i in range(0, len(student_pdfs), bundle_size)]
    for n, chunk in enumerate(chunks, 1):
        out = build_dir / f'{job_name}-bundle-{n}.pdf'
        bundle_pdfs(chunk, out, two_sided=two_sided)
        print(f'Bundle {n}/{len(chunks)}: {out.name} ({len(chunk)} exams, two_sided={two_sided})')


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
