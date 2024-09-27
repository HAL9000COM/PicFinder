# -*- coding: utf-8 -*-
import os
import sys
import tempfile

temp_dir = tempfile.gettempdir()

is_nuitka = "__compiled__" in globals()
if sys.stdout is None or is_nuitka:
    # sys.stdout = open(os.devnull, "w")
    sys.stdout = open(os.path.join(temp_dir, "stdout.log"), "w")
if sys.stderr is None or is_nuitka:
    # sys.stderr = open(os.devnull, "w")
    sys.stderr = open(os.path.join(temp_dir, "stderr.log"), "w")
import logging
from multiprocessing import freeze_support

from PySide6.QtGui import QIcon
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
    window.setWindowIcon(QIcon("icon.ico"))
    window.show()
    code = app.exec()
    os._exit(code)
