"""
Distribute built exam PDFs to students.

Reads a Blackboard Learn gradebook CSV, assigns exam versions to students
round-robin, creates per-student output folders, and optionally emails
exams via Outlook COM automation.
"""

from __future__ import annotations

import logging
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


def discover_exams(build_dir: Path) -> Dict[int, Tuple[Path, Optional[Path]]]:
    """
    Scan *build_dir* for exam and solution PDFs.

    Detects files matching ``<jobname>-<serial>.pdf`` and pairs them
    with ``<jobname>_soln-<serial>.pdf`` when present.

    Parameters
    ----------
    build_dir : Path
        Directory containing built exam PDFs.

    Returns
    -------
    dict
        Mapping of serial (int) to ``(exam_path, soln_path_or_None)``,
        sorted by serial number.
    """
    all_pdfs = sorted(build_dir.glob("*.pdf"))

    # Greedy prefix handles job-names that contain hyphens
    soln_pattern = re.compile(r"^(.+)_soln-(\d+)\.pdf$")
    exam_pattern = re.compile(r"^(.+)-(\d+)\.pdf$")

    # First pass: collect solution files
    soln_files: Dict[int, Path] = {}
    for pdf in all_pdfs:
        m = soln_pattern.match(pdf.name)
        if m:
            serial = int(m.group(2))
            soln_files[serial] = pdf

    # Second pass: collect exam files (skip solutions)
    exams: Dict[int, Tuple[Path, Optional[Path]]] = {}
    for pdf in all_pdfs:
        if soln_pattern.match(pdf.name):
            continue
        m = exam_pattern.match(pdf.name)
        if m:
            serial = int(m.group(2))
            exams[serial] = (pdf, soln_files.get(serial))

    return dict(sorted(exams.items()))


def read_gradebook(
    gradebook_path: Path,
    filter_column: Optional[str] = None,
) -> pd.DataFrame:
    """
    Read a Blackboard Learn gradebook CSV and return a filtered, sorted
    DataFrame of students.

    Parameters
    ----------
    gradebook_path : Path
        Path to the CSV file.
    filter_column : str or None
        If specified, only include rows where this column's value
        is ``"yes"`` or ``"true"`` (case-insensitive).

    Returns
    -------
    pd.DataFrame
        Sorted by ("Last Name", "First Name").
    """
    df = pd.read_csv(gradebook_path, dtype=str, index_col=False).fillna("")

    # Drop unnamed columns (common Blackboard CSV artifact)
    unnamed_cols = [c for c in df.columns if c.startswith("Unnamed")]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols)

    for col in ("Last Name", "First Name", "Username"):
        if col not in df.columns:
            raise ValueError(
                f"Gradebook missing required column '{col}'. "
                f"Columns found: {df.columns.tolist()}"
            )

    if filter_column:
        if filter_column not in df.columns:
            raise ValueError(
                f"Filter column '{filter_column}' not found in gradebook. "
                f"Columns found: {df.columns.tolist()}"
            )
        mask = df[filter_column].str.strip().str.lower().isin(("yes", "true"))
        df = df[mask]

    df = df.sort_values(["Last Name", "First Name"], ignore_index=True)
    return df


def distribute_exams(
    build_dir: Path | str,
    gradebook_path: Path | str,
    output_dir: Path | str = "distributed",
    filter_column: Optional[str] = None,
    email: bool = False,
    email_suffix: str = "@drexel.edu",
    subject: str = "Your exam",
    body: str = (
        "Attached is your exam. "
        "Please contact your instructor with any questions."
    ),
    dry_run: bool = False,
    include_solutions: bool = True,
) -> int:
    """
    Assign exam versions to students round-robin and create per-student
    output folders.  Optionally email exams via Outlook.

    Parameters
    ----------
    build_dir : Path or str
        Directory containing built exam PDFs.
    gradebook_path : Path or str
        Blackboard Learn gradebook CSV.
    output_dir : Path or str
        Root directory for per-student subfolders.
    filter_column : str or None
        Column name where ``"yes"``/``"true"`` selects students.
    email : bool
        If True, send exams via Outlook COM automation.
    email_suffix : str
        Appended to the Username column to form email addresses.
    subject : str
        Email subject line.
    body : str
        Plain-text email body.
    dry_run : bool
        If True, preview email actions without sending.
    include_solutions : bool
        If True (default), include solution PDFs in student folders
        and email attachments.  If False, only the exam PDF is distributed.

    Returns
    -------
    int
        0 on success, 1 on error.
    """
    build_dir = Path(build_dir)
    gradebook_path = Path(gradebook_path)
    output_dir = Path(output_dir)

    # ---- 1. Discover exams ----
    if not build_dir.is_dir():
        print(f"Build directory does not exist: {build_dir}")
        return 1

    exams = discover_exams(build_dir)
    if not exams:
        print(f"No exam PDFs found in {build_dir}")
        return 1

    serials = list(exams.keys())
    has_solutions = any(soln is not None for _, soln in exams.values())
    n_soln = sum(1 for _, soln in exams.values() if soln is not None)
    print(f"Found {len(serials)} exam version(s) in {build_dir}")
    if has_solutions:
        print(f"  ({n_soln} with solution PDFs)")

    # ---- 2. Read gradebook ----
    if not gradebook_path.is_file():
        print(f"Gradebook not found: {gradebook_path}")
        return 1

    students = read_gradebook(gradebook_path, filter_column)
    if students.empty:
        print("No students found (after filtering). Nothing to do.")
        return 1

    print(f"Found {len(students)} student(s) in gradebook")

    # ---- 3. Round-robin assignment ----
    assignments: List[dict] = []
    for i, (_, row) in enumerate(students.iterrows()):
        serial = serials[i % len(serials)]
        exam_path, soln_path = exams[serial]
        assignments.append({
            "last_name": row["Last Name"].strip(),
            "first_name": row["First Name"].strip(),
            "username": row["Username"].strip(),
            "serial": serial,
            "exam_path": exam_path,
            "soln_path": soln_path,
        })

    # ---- 4. Create output folders and copy files ----
    output_dir.mkdir(parents=True, exist_ok=True)

    for a in assignments:
        folder_name = f"{a['last_name']}, {a['first_name']}"
        student_dir = output_dir / folder_name
        student_dir.mkdir(parents=True, exist_ok=True)

        shutil.copy2(a["exam_path"], student_dir / a["exam_path"].name)
        if include_solutions and a["soln_path"] is not None:
            shutil.copy2(a["soln_path"], student_dir / a["soln_path"].name)

    print(f"Created {len(assignments)} student folder(s) in {output_dir}")

    # ---- 5. Email (optional) ----
    if email:
        if not dry_run:
            import win32com.client
            outlook = win32com.client.Dispatch("Outlook.Application")

        sent = 0
        failed = []

        for a in assignments:
            addr = a["username"] + email_suffix

            if dry_run:
                print(f"  [DRY RUN] To: {addr}")
                print(f"            Exam: {a['exam_path'].name}")
                if include_solutions and a["soln_path"]:
                    print(f"            Soln: {a['soln_path'].name}")
                print()
                sent += 1
                continue

            try:
                mail = outlook.CreateItem(0)
                mail.To = addr
                mail.Subject = subject
                mail.Body = body
                mail.Attachments.Add(str(a["exam_path"].resolve()))
                if include_solutions and a["soln_path"]:
                    mail.Attachments.Add(str(a["soln_path"].resolve()))
                mail.Send()
                sent += 1
                sys.stderr.write(f"\rSent {sent}...")
                sys.stderr.flush()
            except Exception as e:
                failed.append((a["username"], addr, str(e)))
                logger.error(f"Failed to send to {addr}: {e}")

        sys.stderr.write("\r" + " " * 40 + "\r")
        sys.stderr.flush()

        prefix = "[DRY RUN] " if dry_run else ""
        print(f"\n{prefix}Email summary:")
        print(f"  {prefix}Emails sent: {sent}")
        if failed:
            print(f"  Failed: {len(failed)}")
            for uname, addr, err in failed:
                print(f"    {uname} ({addr}): {err}")

    # ---- 6. Summary report ----
    print(f"\n{'Student':<40s} {'Serial':>10s}")
    print(f"{'-'*40} {'-'*10}")
    for a in assignments:
        name = f"{a['last_name']}, {a['first_name']}"
        print(f"{name:<40s} {a['serial']:>10d}")

    return 0


def distribute_subcommand(args) -> int:
    """CLI entry point for the ``distribute`` subcommand."""
    return distribute_exams(
        build_dir=args.build_dir,
        gradebook_path=args.gradebook,
        output_dir=args.output_dir,
        filter_column=args.filter_column,
        email=args.email,
        email_suffix=args.email_suffix,
        subject=args.subject,
        body=args.body,
        dry_run=args.dry_run,
        include_solutions=args.include_solutions,
    )
