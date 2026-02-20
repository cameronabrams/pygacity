# Author: Cameron F. Abrams, <cfa22@drexel.edu>

import logging
import os
import shutil

import argparse as ap

from .generate.build import build, answerset_subcommand
from .util.distribute import distribute_subcommand
from .util.pdfutils import combine_pdfs
from .util.stringthings import oxford, banner

logger = logging.getLogger(__name__)

def setup_logging(args):    
    loglevel_numeric = getattr(logging, args.logging_level.upper())
    if args.log:
        if os.path.exists(args.log):
            shutil.copyfile(args.log, args.log+'.bak')
        logging.basicConfig(filename=args.log,
                            filemode='w',
                            format='%(asctime)s %(name)s %(message)s',
                            level=loglevel_numeric
        )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s> %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def cli():
    subcommands = {
        'build': dict(
            func = build,
            help = 'build document',
            ),
        'answerset' : dict(
            func = answerset_subcommand,
            help = 'remake answer set document from a previous build',
        ),
        'combine': dict(
            func = combine_pdfs,
            help = 'combine PDFs',
        ),
        'singlet': dict(
            func = build,
            help = 'build a single problem'
        ),
        'distribute': dict(
            func = distribute_subcommand,
            help = 'distribute built exam PDFs to students',
        ),
    }
    parser = ap.ArgumentParser(
        prog='pygacity',
        description='pygacity -- build customized engineering assignment/exam documents',
        epilog='(c) 2025 Cameron F. Abrams <cfa22@drexel.edu>'
    )
    parser.add_argument(
        '-b',
        '--banner',
        default=False,
        action=ap.BooleanOptionalAction,
        help='toggle banner message'
    )
    parser.add_argument(
        '--logging-level',
        type=str,
        default='debug',
        choices=[None, 'info', 'debug', 'warning'],
        help='Logging level for messages written to diagnostic log'
    )
    parser.add_argument(
        '-l',
        '--log',
        type=str,
        default='pygacity-diagnostics.log',
        help='File to which diagnostic log messages are written'
    )
    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="command",
        metavar="<command>",
        required=True,
    )
    command_parsers={}
    for k, specs in subcommands.items():
        command_parsers[k] = subparsers.add_parser(
            k,
            help=specs['help'],
            formatter_class=ap.RawDescriptionHelpFormatter
        )
        command_parsers[k].set_defaults(func=specs['func'])

    command_parsers['build'].add_argument(
        '-o',
        '--overwrite',
        type=bool,
        default=False,
        action=ap.BooleanOptionalAction,
        help='completely remove old save dir and build new exams')
    command_parsers['build'].add_argument(
        'f',
        help='mandatory YAML input file')
    command_parsers['answerset'].add_argument(
        'f',
        help='mandatory YAML input file used in a previous build to generate the answer set')
    command_parsers['combine'].add_argument(
        '-i',
        '--input-pdfs',
        type=str,
        default=[],
        nargs='+',  
        help='space-separated list of PDF file names to combine'
    )
    command_parsers['combine'].add_argument(
        '-o',
        '--pdf-out',
        type=str,
        default='out.pdf',
        help='name of new output PDF to be created')
    command_parsers['singlet'].add_argument(
        '-t',
        '--texfile',
        type=str,
        help='name of tex file containing single problem'
    )
    command_parsers['singlet'].add_argument(
        '-o',
        '--overwrite',
        type=bool,
        default=True,
        action=ap.BooleanOptionalAction,
        help='completely remove old save dir and build new exams')
    command_parsers['distribute'].add_argument(
        'build_dir',
        help='directory containing built exam PDFs')
    command_parsers['distribute'].add_argument(
        'gradebook',
        help='path to Blackboard Learn gradebook CSV')
    command_parsers['distribute'].add_argument(
        '-o',
        '--output-dir',
        type=str,
        default='distributed',
        help='root directory for per-student subfolders (default: distributed/)')
    command_parsers['distribute'].add_argument(
        '-fc',
        '--filter-column',
        type=str,
        default=None,
        help='gradebook column where "yes" or "true" selects students to receive exams')
    command_parsers['distribute'].add_argument(
        '--email',
        default=False,
        action=ap.BooleanOptionalAction,
        help='send exams to students via Outlook')
    command_parsers['distribute'].add_argument(
        '--email-suffix',
        type=str,
        default='@drexel.edu',
        help='suffix appended to Username for email address (default: @drexel.edu)')
    command_parsers['distribute'].add_argument(
        '--subject',
        type=str,
        default='Your exam',
        help='email subject line')
    command_parsers['distribute'].add_argument(
        '--body',
        type=str,
        default='Attached is your exam. Please contact your instructor with any questions.',
        help='plain-text email body')
    command_parsers['distribute'].add_argument(
        '--dry-run',
        default=False,
        action=ap.BooleanOptionalAction,
        help='preview email actions without actually sending')
    command_parsers['distribute'].add_argument(
        '--include-solutions',
        default=True,
        action=ap.BooleanOptionalAction,
        help='include solution PDFs in student folders and emails (default: yes; use --no-include-solutions to omit)')
    args = parser.parse_args()

    setup_logging(args)

    if args.banner:
        banner(print)    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        my_list = oxford(list(subcommands.keys()))
        print(f'No subcommand found. Expected one of {my_list}')
    logger.info('Thanks for using pygacity!')
