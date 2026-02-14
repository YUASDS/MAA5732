import re

# PIPE
from subprocess import run as adb_run, DEVNULL, PIPE
from src.utils.configs import cfg as cfg


def change_size(adb_adress):
    result = adb_run(
        [cfg.adb_dir, "-s", adb_adress, "shell", "wm", "size"],
        stdout=PIPE,
        stderr=PIPE,
    )
    pat = re.compile(r"\d{1,5}")
    width, height = pat.findall(result.stdout.decode())
    cfg.width, cfg.height = int(width), int(height)


def restart():
    adb_run(
        [cfg.adb_dir, "kill-server"],
        stdout=PIPE,
        stderr=PIPE,
    )
    adb_run(
        [cfg.adb_dir, "start-server"],
        stdout=PIPE,
        stderr=PIPE,
    )
