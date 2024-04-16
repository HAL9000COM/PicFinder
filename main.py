# -*- coding: utf-8 -*-

import logging
import os
import sys
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
