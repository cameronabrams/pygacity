import argparse as ap

from .build import build
from .pdfutils import combine_pdfs
from .stringthings import oxford, banner

def cli():
    subcommands={
        'build': dict(func=build,help='build document',desc='builds a document according to specs in a YAML config file'),
        'combine':dict(func=combine_pdfs,help='combine PDFs into a single PDF',desc='combine PDFs into a single PDF')
    }
    parser=ap.ArgumentParser()#description=textwrap.dedent(banner_message),formatter_class=ap.RawDescriptionHelpFormatter)
    parser.add_argument('--no-banner',default=False,action='store_true',help='turn off the banner')
    subparsers=parser.add_subparsers()
    subparsers.required=False
    command_parsers={}
    for k,specs in subcommands.items():
        command_parsers[k]=subparsers.add_parser(k,description=specs['desc'],help=specs['help'],formatter_class=ap.RawDescriptionHelpFormatter)
        command_parsers[k].set_defaults(func=specs['func'])
    command_parsers['build'].add_argument('--overwrite',default=False,action=ap.BooleanOptionalAction,help='completely remove old save dir and build new exams')
    command_parsers['build'].add_argument('--solutions',default=True,action=ap.BooleanOptionalAction,help='build solutions')
    command_parsers['build'].add_argument('f',help='mandatory YAML input file')
    command_parsers['combine'].add_argument('-i',type=str,default=[],nargs='+',help='space-separated list of PDF file names to combine')
    command_parsers['combine'].add_argument('-o',type=str,default='',help='name of new output PDF to created')

    args=parser.parse_args()
    if not args.no_banner:
        banner(print)    
    if hasattr(args,'func'):
        args.func(args)
    else:
        my_list=oxford(list(subcommands.keys()))
        print(f'No subcommand found. Expected one of {my_list}')
