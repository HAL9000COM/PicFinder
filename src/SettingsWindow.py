# -*- coding: utf-8 -*-

import logging
from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QWidget

from SettingsWindow_ui import Ui_Settings


class SettingsWindow(QWidget, Ui_Settings):
    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.setupUi(self)
        self.get_models()
        self.settings = QSettings("HAL9000COM", "PicFinder")
        self.load_settings()
        self.pushButton_save.clicked.connect(self.gui_save)
        self.comboBox_object_detection_model.currentIndexChanged.connect(
            self.check_models
        )

    def get_models(self):
        model_dir = Path(__file__).parent / "models"
        self.models_cls = []
        self.models_coco = []
        self.models_oiv = []

        model_files = {
            "YOLOv8n": ["yolov8n.onnx", "yolov8n-cls.onnx", "yolov8n-oiv7.onnx"],
            "YOLOv8s": ["yolov8s.onnx", "yolov8s-cls.onnx", "yolov8s-oiv7.onnx"],
            "YOLOv8m": ["yolov8m.onnx", "yolov8m-cls.onnx", "yolov8m-oiv7.onnx"],
            "YOLOv8l": ["yolov8l.onnx", "yolov8l-cls.onnx", "yolov8l-oiv7.onnx"],
            "YOLOv8x": ["yolov8x.onnx", "yolov8x-cls.onnx", "yolov8x-oiv7.onnx"],
        }

        for model, files in model_files.items():
            if Path(model_dir / files[0]).exists():
                self.models_cls.append(model)
            if Path(model_dir / files[1]).exists():
                self.models_coco.append(model)
            if Path(model_dir / files[2]).exists():
                self.models_oiv.append(model)

        self.comboBox_classification_model.addItems(self.models_cls)
        self.comboBox_object_detection_model.addItems(
            model for model in self.models_coco
        )
        self.comboBox_object_detection_model.addItems(
            model for model in self.models_oiv if model not in self.models_coco
        )

    def check_models(self):
        self.object_detection_model = self.comboBox_object_detection_model.currentText()

        if self.object_detection_model not in self.models_coco:
            self.checkBox_COCO.setChecked(False)
            self.checkBox_COCO.setEnabled(False)
        else:
            self.checkBox_COCO.setEnabled(True)

        if self.object_detection_model not in self.models_oiv:
            self.checkBox_OpenImage.setChecked(False)
            self.checkBox_OpenImage.setEnabled(False)
        else:
            self.checkBox_OpenImage.setEnabled(True)
        self.object_detection_dataset = []
        if self.checkBox_COCO.isChecked():
            self.object_detection_dataset.append("COCO")
        if self.checkBox_OpenImage.isChecked():
            self.object_detection_dataset.append("OpenImage")

    def load_settings(self):
        self.classification_model = self.settings.value(
            "classification_model", "YOLOv8n"
        )
        if self.classification_model not in self.models_cls:
            self.classification_model = "None"
        self.comboBox_classification_model.setCurrentText(self.classification_model)
        self.doubleSpinBox_classification_threshold.setValue(
            float(self.settings.value("classification_threshold", 0.7))
        )
        self.object_detection_model = self.settings.value(
            "object_detection_model", "YOLOv8n"
        )
        if (
            self.object_detection_model not in self.models_coco
            and self.object_detection_model not in self.models_oiv
        ):
            self.object_detection_model = "None"
        self.comboBox_object_detection_model.setCurrentText(self.object_detection_model)

        self.object_detection_dataset = self.settings.value(
            "object_detection_dataset", ["COCO"]
        )

        if "COCO" in self.object_detection_dataset:
            self.checkBox_COCO.setChecked(True)
        else:
            self.checkBox_COCO.setChecked(False)
        if "OpenImage" in self.object_detection_dataset:
            self.checkBox_OpenImage.setChecked(True)
        else:
            self.checkBox_OpenImage.setChecked(False)

        self.check_models()
        self.doubleSpinBox_object_detection_confidence.setValue(
            float(self.settings.value("object_detection_conf_threshold", 0.7))
        )
        self.doubleSpinBox_object_detection_iou.setValue(
            float(self.settings.value("object_detection_iou_threshold", 0.5))
        )
        self.comboBox_OCR_model.setCurrentText(
            self.settings.value("OCR_model", "RapidOCR")
        )
        self.checkBox_update.setChecked(
            self.settings.value("FullUpdate", False, type=bool)
        )
        self.spinBox_batch_size.setValue(int(self.settings.value("batch_size", 100)))
        self.save_settings()

    def save_settings(self):
        self.check_models()
        self.settings.setValue(
            "classification_model", self.comboBox_classification_model.currentText()
        )
        self.settings.setValue(
            "classification_threshold",
            self.doubleSpinBox_classification_threshold.value(),
        )
        self.settings.setValue(
            "object_detection_model",
            self.comboBox_object_detection_model.currentText(),
        )
        self.settings.setValue(
            "object_detection_dataset", self.object_detection_dataset
        )
        self.settings.setValue(
            "object_detection_conf_threshold",
            self.doubleSpinBox_object_detection_confidence.value(),
        )
        self.settings.setValue(
            "object_detection_iou_threshold",
            self.doubleSpinBox_object_detection_iou.value(),
        )
        self.settings.setValue("OCR_model", self.comboBox_OCR_model.currentText())
        self.settings.setValue("FullUpdate", self.checkBox_update.isChecked())
        self.settings.setValue("batch_size", self.spinBox_batch_size.value())

    def gui_save(self):
        self.save_settings()
        self.close()
