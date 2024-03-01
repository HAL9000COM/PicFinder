# -*- coding: utf-8 -*-

from pathlib import Path

from PySide6.QtWidgets import QApplication, QFileDialog, QMainWindow

from backend.image_process import read_img
from MainWindow_ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setAcceptDrops(True)
        self.pushButton_folder_browse.clicked.connect(self.browse_folder)
        self.pushButton_index.clicked.connect(self.index_folder)

    def browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.lineEdit_folder.setText(path)

    def index_folder(self):
        self.folder_path = Path(self.lineEdit_folder.text())
        if self.folder_path.exists() and self.folder_path.is_dir():
            self.index_folder_path(self.folder_path)
        else:
            self.statusbar.showMessage("Invalid Folder Path")

    def index_folder_path(self, folder_path: Path):
        # list all files in the folder and subfolders
        file_list = folder_path.rglob("*")
        for file in folder_path.rglob("*"):
            if file.is_file():
                # read the image
                # img = read_img(file)
                # print(img)
                # get relative path
                print(file.relative_to(folder_path))
        pass

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            # decide where is the mouse position
            if self.lineEdit_folder.underMouse():
                # check if the dropped file is a directory
                url = Path(url.toLocalFile())
                if url.is_dir():
                    self.lineEdit_folder.setText(url.as_posix())
                else:
                    self.statusbar.showMessage("Invalid Folder Path", 3000)
            else:
                event.ignore()
