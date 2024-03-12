# -*- coding: utf-8 -*-

import logging
from multiprocessing import Pool
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QFileDialog, QMainWindow

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

    def lineEdit_folder_textChanged(self, text):
        if text:
            self.pushButton_index.setEnabled(True)
        else:
            self.pushButton_index.setEnabled(False)
        self.folder_path = Path(text)

    def browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.lineEdit_folder.setText(path)

    def index_folder(self):
        if self.folder_path.exists() and self.folder_path.is_dir():

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
            self.statusbar.showMessage("Indexing...", 3000)

        else:
            self.statusbar.showMessage("Invalid Folder Path")

    def index_progress(self, value):
        self.statusbar.showMessage(f"Indexing... {value}%")

    def index_finished(self):
        self.statusbar.showMessage("Indexing Finished", 3000)

    def search(self):
        query = self.lineEdit_search.text()
        if query:
            db_path = self.folder_path / "PicFinder.db"
            if db_path.exists():
                self.search_worker = SearchWorker(db_path, query)
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
                self.statusbar.showMessage("Searching...", 3000)
            else:
                self.statusbar.showMessage("Database not found", 3000)

    def search_finished(self):
        self.statusbar.showMessage("Search Finished", 3000)

    def search_result(self, result):
        # self.listWidget_search_result.clear()
        # for file in result:
        #     self.listWidget_search_result.addItem(file[1])
        logging.debug(result)

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
