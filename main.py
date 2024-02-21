# -*- coding: utf-8 -*-
import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTranslator
from MainWindow import MainWindow
import logging
from multiprocessing import freeze_support

import traceback
import importlib.resources


if __name__ == "__main__":
    freeze_support()

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    code = app.exec()
    traceback.print_exc()
    os._exit(code)
