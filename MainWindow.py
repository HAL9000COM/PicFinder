# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QApplication, QMainWindow

from MainWindow_ui import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
