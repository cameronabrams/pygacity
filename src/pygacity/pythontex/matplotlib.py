from pathlib import Path
import os
import matplotlib
import matplotlib.pyplot as plt
import logging

safe_mplconfig = Path.cwd() / "_mplconfig"
safe_mplconfig.mkdir(exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(safe_mplconfig)

matplotlib.use("Agg")

logging.getLogger("matplotlib").setLevel(logging.WARNING)
