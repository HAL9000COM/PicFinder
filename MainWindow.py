# -*- coding: utf-8 -*-

import logging
from multiprocessing import Pool
from pathlib import Path

from PySide6.QtCore import QObject, QSize, Qt, QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import QFileDialog, QListWidget, QListWidgetItem, QMainWindow

from backend.db_ops import DB
from backend.image_process import read_img_warper
from MainWindow_ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setAcceptDrops(True)

        self.pushButton_folder_browse.clicked.connect(self.browse_folder)
        self.pushButton_index.clicked.connect(self.index_folder)
        self.pushButton_search.clicked.connect(self.search)

        self.lineEdit_folder.textChanged.connect(self.lineEdit_folder_textChanged)

        self.lineEdit_search.returnPressed.connect(self.search)

        self.listWidget_search_result.setViewMode(QListWidget.IconMode)
        self.listWidget_search_result.setIconSize(QSize(300, 300))
        self.listWidget_search_result.setResizeMode(QListWidget.Adjust)
        self.listWidget_search_result.setWordWrap(True)
        self.listWidget_search_result.setFlow(QListWidget.LeftToRight)
        self.listWidget_search_result.setWrapping(True)
        self.listWidget_search_result.setGridSize(QSize(320, 320))
        self.listWidget_search_result.setSpacing(20)
        self.listWidget_search_result.setUniformItemSizes(True)
        self.listWidget_search_result.setTextElideMode(Qt.ElideNone)
        self.listWidget_search_result.setWordWrap(True)
        self.listWidget_search_result.itemDoubleClicked.connect(self.open_file)

        self.folder_path = Path()

        self.pushButton_index.setEnabled(False)
        self.pushButton_search.setEnabled(False)

    def lineEdit_folder_textChanged(self, text):
        if text:
            self.pushButton_index.setEnabled(True)
        else:
            self.pushButton_index.setEnabled(False)
        self.folder_path = Path(text)
        self.db_path = self.folder_path / "PicFinder.db"
        self.listWidget_search_result.clear()
        if self.db_exists_check():
            self.statusbar.showMessage(
                f"Folder: {self.folder_path.as_posix()} , Index Found"
            )
        else:
            self.statusbar.showMessage(
                f"Folder: {self.folder_path.as_posix()} , Index Not Found"
            )

    def db_exists_check(self):
        if self.db_path.exists():
            self.pushButton_search.setEnabled(True)
            return True
        else:
            self.pushButton_search.setEnabled(False)
            return False

    def browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.lineEdit_folder.setText(path)

    def index_folder(self):
        if self.folder_path.exists() and self.folder_path.is_dir():

            self.pushButton_index.setEnabled(False)
            self.pushButton_search.setEnabled(False)
            self.listWidget_search_result.clear()

            self.index_worker = IndexWorker(self.folder_path)
            self.index_worker_thread = QThread()
            self.index_worker.moveToThread(self.index_worker_thread)
            self.index_worker_thread.started.connect(self.index_worker.run)
            self.index_worker.finished.connect(self.index_finished)
            self.index_worker.finished.connect(self.index_worker_thread.quit)
            self.index_worker.finished.connect(self.index_worker.deleteLater)
            self.index_worker_thread.finished.connect(
                self.index_worker_thread.deleteLater
            )
            self.index_worker.progress.connect(self.index_progress)
            self.index_worker_thread.start()
            self.statusbar.showMessage("Indexing...")
        else:
            self.statusbar.showMessage("Invalid Folder Path")

    def index_progress(self, value):
        self.statusbar.showMessage(f"Indexing... {value}%")

    def index_finished(self):
        self.statusbar.showMessage("Indexing Finished")
        self.db_exists_check()
        self.pushButton_index.setEnabled(True)

    def search(self):
        query = self.lineEdit_search.text()
        if query:
            if self.db_exists_check() and self.pushButton_search.isEnabled():
                self.pushButton_search.setEnabled(False)
                self.search_worker = SearchWorker(self.db_path, query)
                self.search_worker_thread = QThread()
                self.search_worker.moveToThread(self.search_worker_thread)
                self.search_worker_thread.started.connect(self.search_worker.run)
                self.search_worker.finished.connect(self.search_finished)
                self.search_worker.finished.connect(self.search_worker_thread.quit)
                self.search_worker.finished.connect(self.search_worker.deleteLater)
                self.search_worker_thread.finished.connect(
                    self.search_worker_thread.deleteLater
                )
                self.search_worker.result.connect(self.search_result)
                self.search_worker_thread.start()
                self.statusbar.showMessage("Searching...")
            else:
                self.statusbar.showMessage("Database not found")

    def search_finished(self):
        self.statusbar.showMessage("Search Finished")
        self.pushButton_search.setEnabled(True)

    def search_result(self, result):
        # self.listWidget_search_result.clear()
        # for file in result:
        #     self.listWidget_search_result.addItem(file[1])
        logging.debug(result)
        self.populate_list(result)

    def populate_list(self, result):
        self.listWidget_search_result.clear()
        for file in result:
            file_path = self.folder_path / Path(file[2])
            file_classification = file[3]
            file_classification_confidence = file[4]
            file_object = file[5]
            file_object_confidence = file[6]
            file_ocr = file[7]
            file_ocr_confidence = file[8]

            file_info = (
                f"File: {file_path.as_posix()}\n"
                f"Classification: {file_classification} ({file_classification_confidence:.2f})\n"
                f"Object: {file_object} ({file_object_confidence:.2f})\n"
                f"OCR: {file_ocr} ({file_ocr_confidence:.2f})"
            )

            item = QListWidgetItem()
            item.setIcon(QIcon(file_path.as_posix()))
            item.setText(file[2])

            item.setToolTip(file_info)

            self.listWidget_search_result.addItem(item)

    def open_file(self, item: QListWidgetItem):
        file_path = self.folder_path / Path(item.text())
        url = QUrl.fromLocalFile(file_path)
        QDesktopServices.openUrl(url)

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


class IndexWorker(QObject):
    finished = Signal()
    progress = Signal(int)

    def __init__(self, folder_path: Path):
        super(IndexWorker, self).__init__()
        self.folder = folder_path

    def read_folder(self, folder_path: Path, **kwargs):
        # list all files in the folder and subfolders
        file_list = [file for file in folder_path.rglob("*") if file.is_file()]
        input_list = [(file, kwargs) for file in file_list]

        with Pool() as p:
            total_files = len(file_list)
            for i, result in enumerate(
                p.imap(read_img_warper, input_list, chunksize=1)
            ):
                self.progress.emit(int((i + 1) / total_files * 100))
                yield result

    def run(self):
        db_path = self.folder / "PicFinder.db"
        if db_path.exists():
            db_path.unlink()

        results = self.read_folder(self.folder)

        db = DB(db_path)

        for result in results:
            logging.debug(result)
            if "error" in result.keys():
                continue

            rel_path = Path(result["path"]).relative_to(self.folder).as_posix()

            if result["classification"] is None:
                classification = ""
                classification_confidence_avg = 0
            else:
                classification = " ".join([res[0] for res in result["classification"]])
                classification_confidence_list = [
                    res[1] for res in result["classification"]
                ]
                classification_confidence_avg = sum(
                    classification_confidence_list  # type: ignore
                ) / len(classification_confidence_list)

            if result["object_detection"] is None:
                object = ""
                object_confidence_avg = 0
            else:
                object = " ".join([res[0] for res in result["object_detection"]])
                object_confidence_list = [res[1] for res in result["object_detection"]]
                object_confidence_avg = sum(
                    object_confidence_list  # type: ignore
                ) / len(object_confidence_list)

            if result["OCR"] is None:
                OCR = ""
                ocr_confidence_avg = 0
            else:
                OCR = " ".join([res[0] for res in result["OCR"]])
                ocr_confidence_list = [res[1] for res in result["OCR"]]
                ocr_confidence_avg = sum(ocr_confidence_list) / len(ocr_confidence_list)  # type: ignore

            db.insert(
                result["hash"],
                rel_path,
                classification,
                classification_confidence_avg,
                object,
                object_confidence_avg,
                OCR,
                ocr_confidence_avg,
            )
        db.close()
        self.finished.emit()


class SearchWorker(QObject):
    finished = Signal()
    progress = Signal(int)
    result = Signal(list)

    def __init__(self, db_path: Path, query: str):
        super(SearchWorker, self).__init__()
        self.db = DB(db_path)
        self.query = query

    def run(self):
        result = self.db.search(self.query)
        self.db.close()
        self.finished.emit()
        self.result.emit(result)
