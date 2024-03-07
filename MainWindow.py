# -*- coding: utf-8 -*-

from multiprocessing import Pool
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QFileDialog, QMainWindow
from tqdm import tqdm

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

    def browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.lineEdit_folder.setText(path)

    def index_folder(self):
        self.folder_path = Path(self.lineEdit_folder.text())
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
            # self.index_worker.progress.connect(self.progressBar.setValue)
            self.index_worker_thread.start()
            self.statusbar.showMessage("Indexing...", 3000)

        else:
            self.statusbar.showMessage("Invalid Folder Path")

    def index_finished(self):
        self.statusbar.showMessage("Indexing Finished", 3000)

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
            res = list(tqdm(p.imap(read_img_warper, input_list), total=len(file_list)))

        return res

    def run(self):
        db = DB(self.folder / "PicFinder.db")

        results = self.read_folder(self.folder)
        for result in results:
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
                    classification_confidence_list
                ) / len(classification_confidence_list)

            if result["object_detection"] is None:
                object = ""
                object_confidence_avg = 0
            else:
                object = " ".join([res[0] for res in result["object_detection"]])
                object_confidence_list = [res[1] for res in result["object_detection"]]
                object_confidence_avg = sum(object_confidence_list) / len(
                    object_confidence_list
                )

            if result["OCR"] is None:
                OCR = ""
                ocr_confidence_avg = 0
            else:
                OCR = " ".join([res[0] for res in result["OCR"]])
                ocr_confidence_list = [res[1] for res in result["OCR"]]
                ocr_confidence_avg = sum(ocr_confidence_list) / len(ocr_confidence_list)

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
        self.finished.emit()
