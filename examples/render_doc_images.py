#!/usr/bin/env python
"""
Render documentation images for pygacity examples.

Builds each example with ``pygacity``, converts specific PDF pages to PNG,
and writes them to ``docs/source/_static/examples/``.

Run from the repository root or from the ``examples/`` directory:

    python examples/render_doc_images.py
    python examples/render_doc_images.py --no-build
    python examples/render_doc_images.py --dpi 200

Requirements: poppler (``pdftoppm`` and ``pdfinfo`` must be on PATH).
"""
import argparse
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path


def _require_source_install():
    """Abort if pygacity is not installed as an editable (source) install."""
    try:
        dist = importlib.metadata.distribution('pygacity')
        raw = dist.read_text('direct_url.json')
        if raw:
            data = json.loads(raw)
            if data.get('dir_info', {}).get('editable', False):
                return  # editable install — OK
    except importlib.metadata.PackageNotFoundError:
        pass
    sys.exit(
        'Error: render_doc_images.py requires pygacity to be installed as an '
        'editable source install (pip install -e .).\n'
        'This script writes into the docs/ tree and must not be run from a '
        'distribution install.'
    )

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / 'examples'
STATIC_DIR = REPO_ROOT / 'docs' / 'source' / '_static' / 'examples'


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_build(example_dir: Path, yaml_file: str = None, singlet_file: str = None):
    """Run ``pygacity build`` or ``pygacity singlet`` in *example_dir*."""
    cmd = ['pygacity', 'singlet', singlet_file, '--overwrite'] if singlet_file else ['pygacity', 'build', yaml_file, '--overwrite']
    print(f'\nBuilding {example_dir.name} ...')
    subprocess.run(cmd, cwd=example_dir, check=True)


def pdf_page_count(pdf_path: Path) -> int:
    """Return page count using ``pdfinfo``."""
    result = subprocess.run(
        ['pdfinfo', str(pdf_path)], capture_output=True, text=True, check=True
    )
    for line in result.stdout.splitlines():
        if line.startswith('Pages:'):
            return int(line.split(':', 1)[1].strip())
    raise ValueError(f'Could not determine page count for {pdf_path}')


def render_pages(pdf_path: Path, dest_stem: str, pages: list[int], dpi: int):
    """
    Convert *pages* of *pdf_path* to PNGs named ``{dest_stem}-{page}.png``
    in ``STATIC_DIR``, using ``pdftoppm``.
    """
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    for page in pages:
        tmp_prefix = STATIC_DIR / f'_tmp_{dest_stem}'
        subprocess.run(
            ['pdftoppm', '-r', str(dpi), '-png',
             '-f', str(page), '-l', str(page),
             str(pdf_path), str(tmp_prefix)],
            check=True,
        )
        # pdftoppm writes <prefix>-N.png (zero-padded to minimum needed width)
        candidates = sorted(STATIC_DIR.glob(f'_tmp_{dest_stem}-*.png'))
        if not candidates:
            raise FileNotFoundError(
                f'pdftoppm produced no output for page {page} of {pdf_path}'
            )
        final = STATIC_DIR / f'{dest_stem}-{page}.png'
        candidates[0].replace(final)
        print(f'  {final.name}')


def serial_pdfs(build_dir: Path, pattern: str) -> list[Path]:
    """
    Return PDFs matching *pattern*, sorted by modification time (build order).
    Build order == serial index order used in the documentation.
    """
    return sorted(build_dir.glob(pattern), key=lambda p: p.stat().st_mtime)


# ---------------------------------------------------------------------------
# Per-example render logic
# ---------------------------------------------------------------------------

def render_simple_assignment(dpi: int, build: bool):
    d = EXAMPLES_DIR / 'simple_assignment'
    if build:
        run_build(d, yaml_file='SimpleAssignment.yaml')
    b = d / 'build'
    print('\nRendering simple_assignment ...')
    render_pages(b / 'Assignment.pdf',      'assignment',      [1],    dpi)
    render_pages(b / 'Assignment_soln.pdf', 'assignment_soln', [1, 2], dpi)


def render_compound_exam(dpi: int, build: bool):
    d = EXAMPLES_DIR / 'compound_exam'
    if build:
        run_build(d, yaml_file='CompoundExam.yaml')
    b = d / 'build'
    print('\nRendering compound_exam ...')
    students = serial_pdfs(b, 'ExamI-*.pdf')
    solns    = serial_pdfs(b, 'ExamI_soln-*.pdf')
    if len(students) >= 1:
        render_pages(students[0], 'compound_exam_s1',      [1, 2], dpi)
    if len(students) >= 2:
        render_pages(students[1], 'compound_exam_s2',      [1],    dpi)
    if len(solns) >= 1:
        render_pages(solns[0],    'compound_exam_s1_soln', [1],    dpi)
    render_pages(b / 'answerset.pdf', 'compound_exam_answerset', [1], dpi)


def render_singlet(dpi: int, build: bool):
    d = EXAMPLES_DIR / 'singlet'
    if build:
        run_build(d, singlet_file='radius.tex')
    b = d / 'build_singlet'
    print('\nRendering singlet ...')
    render_pages(b / 'radius-singlet.pdf',      'singlet',      [1], dpi)
    render_pages(b / 'radius-singlet_soln.pdf', 'singlet_soln', [1], dpi)


def render_thermo_exam(dpi: int, build: bool):
    d = EXAMPLES_DIR / 'thermo_exam'
    if build:
        run_build(d, yaml_file='ThermoExam.yaml')
    b = d / 'build'
    print('\nRendering thermo_exam ...')
    students = serial_pdfs(b, 'ExamI-*.pdf')
    solns    = serial_pdfs(b, 'ExamI_soln-*.pdf')
    if len(students) >= 1:
        render_pages(students[0], 'thermo_exam_s1', [1, 2], dpi)
    if len(students) >= 2:
        render_pages(students[1], 'thermo_exam_s2', [1, 2], dpi)
    if len(solns) >= 1:
        n = pdf_page_count(solns[0])
        render_pages(solns[0], 'thermo_exam_s1_soln', list(range(1, n + 1)), dpi)
    render_pages(b / 'answerset.pdf', 'thermo_exam_answerset', [1], dpi)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    _require_source_install()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--no-build', action='store_true',
                        help='Skip building examples; just convert existing PDFs')
    parser.add_argument('--dpi', type=int, default=150,
                        help='PNG resolution in dots per inch (default: 150)')
    parser.add_argument('examples', nargs='*',
                        choices=['simple_assignment', 'compound_exam', 'singlet', 'thermo_exam'],
                        help='Examples to render (default: all)')
    args = parser.parse_args()

    targets = args.examples or ['simple_assignment', 'compound_exam', 'singlet', 'thermo_exam']
    build = not args.no_build

    dispatch = {
        'simple_assignment': render_simple_assignment,
        'compound_exam':     render_compound_exam,
        'singlet':           render_singlet,
        'thermo_exam':       render_thermo_exam,
    }
    for name in targets:
        dispatch[name](dpi=args.dpi, build=build)

    print(f'\nDone. Images written to: {STATIC_DIR}')


if __name__ == '__main__':
    main()
