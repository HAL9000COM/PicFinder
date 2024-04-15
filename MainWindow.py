# -*- coding: utf-8 -*-

import hashlib
import logging
import sys
from multiprocessing import Pool
from pathlib import Path

from PySide6.QtCore import QObject, QSettings, QSize, Qt, QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
)

from backend.db_ops import DB
from backend.image_process import read_img_warper
from MainWindow_ui import Ui_MainWindow
from SettingsWindow import SettingsWindow


class QLogSignal(QObject):
    log = Signal(str)


class QLogHandler(logging.Handler):
    def __init__(self, emitter):
        super().__init__()
        self._emitter = emitter

    @property
    def emitter(self):
        return self._emitter

    def emit(self, record):
        msg = self.format(record)
        self.emitter.log.emit(msg)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setAcceptDrops(True)

        # add actions to menubar
        self.actionSettings = self.menubar.addAction("Settings")
        self.actionAbout = self.menubar.addAction("About")
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionAbout.triggered.connect(self.open_about)

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
        self.listWidget_search_result.setUniformItemSizes(False)
        self.listWidget_search_result.setTextElideMode(Qt.ElideMiddle)
        self.listWidget_search_result.setWordWrap(True)
        self.listWidget_search_result.itemDoubleClicked.connect(self.open_file)

        self.folder_path = Path()

        self.pushButton_index.setEnabled(False)
        self.pushButton_search.setEnabled(False)

        q_log_signal = QLogSignal()

        h = QLogHandler(q_log_signal)
        # set the logger level
        h.setLevel(logging.ERROR)
        logging.getLogger().addHandler(h)
        q_log_signal.log.connect(self.error_pop_up)

        self.update_settings()

    def update_settings(self):
        settings = QSettings("HAL9000COM", "PicFinder")
        self.settings = {}
        self.settings["classification_model"] = settings.value(
            "classification_model", "YOLOv8n"
        )
        self.settings["classification_threshold"] = float(
            settings.value("classification_threshold", 0.7)
        )
        self.settings["object_detection_model"] = settings.value(
            "object_detection_model", "YOLOv8n COCO"
        )
        self.settings["object_detection_conf_threshold"] = float(
            settings.value("object_detection_conf_threshold", 0.7)
        )
        self.settings["object_detection_iou_threshold"] = float(
            settings.value("object_detection_iou_threshold", 0.5)
        )
        self.settings["OCR_model"] = settings.value("OCR_model", "RapidOCR")
        self.settings["AlwaysUpdate"] = settings.value("AlwaysUpdate", False, type=bool)

    def error_pop_up(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def open_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.setWindowTitle("Settings")
        self.settings_window.show()

    def open_about(self):
        pass

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
        try:
            if self.index_worker_thread.isRunning():
                logging.error("Indexing already in progress")
                return
        except:
            pass
        try:
            if self.search_worker_thread.isRunning():
                logging.error("Search in progress, please wait")
                return
        except:
            pass
        self.update_settings()
        if self.folder_path.exists() and self.folder_path.is_dir():

            self.listWidget_search_result.clear()

            self.index_worker = IndexWorker(self.folder_path, **self.settings)
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

    def search(self):
        try:
            if self.search_worker_thread.isRunning():
                logging.error("Search already in progress")
                return
        except:
            pass
        try:
            if self.index_worker_thread.isRunning():
                logging.error("Indexing in progress, please wait")
                return
        except:
            pass
        query = self.lineEdit_search.text()
        if query:
            if self.db_exists_check():
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

    def search_result(self, result):
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

    def __init__(self, folder_path: Path, **kwargs):
        super(IndexWorker, self).__init__()
        self.folder = folder_path
        self.kwargs = kwargs

    def run(self):
        try:
            db_path = self.folder / "PicFinder.db"
            if self.kwargs["AlwaysUpdate"]:
                if db_path.exists():
                    db_path.unlink()
            self.db = DB(db_path)
            results = self.read_folder(self.folder, **self.kwargs)

            for result in results:
                self.save_to_db(result)
            self.db.close()
            self.finished.emit()
        except Exception as e:
            logging.error(e, exc_info=True)
            self.finished.emit()

    def save_to_db(self, result: dict):

        if "error" in result.keys():
            return

        rel_path = Path(result["path"]).relative_to(self.folder).as_posix()

        classification, classification_confidence_avg = self.combine_classification(
            result["classification"]
        )

        object, object_confidence_avg = self.combine_object_detection(
            result["object_detection"]
        )

        OCR, ocr_confidence_avg = self.combine_ocr(result["OCR"])

        self.db.insert(
            result["hash"],
            rel_path,
            classification,
            classification_confidence_avg,
            object,
            object_confidence_avg,
            OCR,
            ocr_confidence_avg,
        )

    def read_folder(self, folder_path: Path, **kwargs):
        # list all files in the folder and subfolders
        file_list = [file for file in folder_path.rglob("*") if file.is_file()]

        # check if file is supported by pillow
        supported_suffix = [
            ".bmp",
            ".jpg",
            ".jpeg",
            ".j2k",
            ".jp2",
            ".jpx",
            ".png",
            ".gif",
            ".tiff",
            ".tif",
            ".webp",
            ".ico",
        ]
        file_list = [
            file for file in file_list if file.suffix.lower() in supported_suffix
        ]

        file_list = [
            file for file in file_list if self.check_file_exists(file) is False
        ]

        input_list = [(file, kwargs) for file in file_list]

        with Pool() as p:
            total_files = len(file_list)
            for i, result in enumerate(
                p.imap(read_img_warper, input_list, chunksize=1)
            ):
                self.progress.emit(int((i + 1) / total_files * 100))
                yield result

    def check_file_exists(self, file_path):
        with open(file_path, "rb") as file:
            img_file = file.read()
            # get md5 hash of image
            img_hash = hashlib.md5(img_file).hexdigest()
            result = self.db.check_hash(img_hash)
            if result:
                return True
            else:
                return False

    def combine_classification(self, classification_list):
        if classification_list is None:
            classification = ""
            classification_confidence_avg = 0
        else:
            classification = " ".join([res[0] for res in classification_list])
            classification_confidence_list = [res[1] for res in classification_list]
            classification_confidence_avg = sum(
                classification_confidence_list  # type: ignore
            ) / len(classification_confidence_list)
        return classification, classification_confidence_avg

    def combine_object_detection(self, object_detection_list):
        if object_detection_list is None:
            object = ""
            object_confidence_avg = 0
        else:
            object = " ".join([res[0] for res in object_detection_list])
            object_confidence_list = [res[1] for res in object_detection_list]
            object_confidence_avg = sum(object_confidence_list) / len(  # type: ignore
                object_confidence_list
            )
        return object, object_confidence_avg

    def combine_ocr(self, ocr_list):
        if ocr_list is None:
            OCR = ""
            ocr_confidence_avg = 0
        else:
            OCR = " ".join([res[0] for res in ocr_list])
            ocr_confidence_list = [res[1] for res in ocr_list]
            ocr_confidence_avg = sum(ocr_confidence_list) / len(ocr_confidence_list)
        return OCR, ocr_confidence_avg


class SearchWorker(QObject):
    finished = Signal()
    progress = Signal(int)
    result = Signal(list)

    def __init__(self, db_path: Path, query: str):
        super(SearchWorker, self).__init__()
        self.db = DB(db_path)
        self.query = query

    def run(self):
        try:
            result = self.db.search(self.query)
            self.db.close()
            self.result.emit(result)
            self.finished.emit()
        except Exception as e:
            logging.error(e, exc_info=True)
            self.finished.emit()
