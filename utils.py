import logging
import os
import sys


def is_admin() -> bool:
    if os.name == 'nt':
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False
    else:
        logging.error("window下使用")
        return os.getuid() == 0


# def launch_win_exe(path: str):
