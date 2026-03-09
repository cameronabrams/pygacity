from shutil import rmtree
import sys
from pathlib import Path
import pickle

pythontex_module = sys.modules['__main__']
logger = getattr(pythontex_module, 'logger', None)
serial = getattr(pythontex_module, 'serial', 0)
logger.debug(f'Pygacity pythontex module teardown begins for serial {serial}.')

safe_mplconfig = getattr(pythontex_module, 'safe_mplconfig', None)
logger.debug(f'Pythontex safe_mplconfig: {safe_mplconfig}')
pythontex_pickle_cache = getattr(pythontex_module, 'pythontex_pickle_cache', None)
logger.debug(f'Pythontex pickle cache: {pythontex_pickle_cache}')
pythontexFC = getattr(pythontex_module, 'pythontexFC', None)
logger.debug(f'Pythontex FileCollector has {len(pythontexFC.data) if pythontexFC is not None else "N/A"} entries.')

AnsSet = getattr(pythontex_module, 'AnsSet', None)
logger.debug(f'Pythontex AnswerSet has {len(AnsSet) if AnsSet is not None else "N/A"} entries.')
logger = getattr(pythontex_module, 'logger', None)
is_solutions = getattr(pythontex_module, 'solutions', False)

if safe_mplconfig is not None:
    logger.debug(f'Removing {safe_mplconfig}')
    rmtree(safe_mplconfig)

if pythontexFC is not None:
    # write this serial's usergenerated files to a pickle for the manager to collect
    userfiles_pickle  = Path(pythontex_pickle_cache) / f"pythontex-usergenerated-files-{serial}.pkl"
    if is_solutions:
        userfiles_pickle = Path(pythontex_pickle_cache) / f"pythontex-solutions-usergenerated-files-{serial}.pkl"
    if len(pythontexFC.data) > 0:
        logger.debug(f'Pickling pythontexFC with {len(pythontexFC.data)} entries for serial {serial} to {userfiles_pickle.as_posix()}.')
        userfiles_pickle.write_bytes(pickle.dumps(pythontexFC, protocol=pickle.HIGHEST_PROTOCOL))
    else:
        logger.debug(f'pythontexFC has no data to pickle for serial {serial}.')
else:
    logger.debug(f'No pythontexFC to pickle for serial {serial}.')

if AnsSet is not None:
    if len(AnsSet) > 0:
        # pickle a non-empty answer set for manager to use
        pkl = Path(pythontex_pickle_cache) / f"answers-{serial}.pkl"
        pkl.write_bytes(pickle.dumps(AnsSet, protocol=pickle.HIGHEST_PROTOCOL))

logger.debug(f'Pygacity pythontex module teardown complete for serial {serial}.')