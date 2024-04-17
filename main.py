# -*- coding: utf-8 -*-


import os
import sys

if sys.stdout is None:
    # sys.stdout = open(os.devnull, "w")
    sys.stdout = open("stdout.log", "w")
if sys.stderr is None:
    # sys.stderr = open(os.devnull, "w")
    sys.stderr = open("stderr.log", "w")
import logging
from multiprocessing import freeze_support

from PySide6.QtWidgets import QApplication

from MainWindow import MainWindow

# set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

if __name__ == "__main__":
    freeze_support()

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    code = app.exec()
    os._exit(code)
