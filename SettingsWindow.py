# -*- coding: utf-8 -*-

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QWidget

from SettingsWindow_ui import Ui_Settings


class SettingsWindow(QWidget, Ui_Settings):
    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.setupUi(self)
        self.settings = QSettings("HAL9000COM", "PicFinder")
        self.load_settings()
        self.pushButton_save.clicked.connect(self.save_settings)

    def load_settings(self):
        self.comboBox_classification_model.setCurrentText(
            self.settings.value("classification_model", "YOLOv8n")
        )
        self.doubleSpinBox_classification_threshold.setValue(
            float(self.settings.value("classification_threshold", 0.7))
        )
        self.comboBox_object_detection_model.setCurrentText(
            self.settings.value("object_detection_model", "YOLOv8n COCO")
        )
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
            self.settings.value("AlwaysUpdate", False, type=bool)
        )

    def save_settings(self):
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
            "object_detection_conf_threshold",
            self.doubleSpinBox_object_detection_confidence.value(),
        )
        self.settings.setValue(
            "object_detection_iou_threshold",
            self.doubleSpinBox_object_detection_iou.value(),
        )
        self.settings.setValue("OCR_model", self.comboBox_OCR_model.currentText())
        self.settings.setValue("AlwaysUpdate", self.checkBox_update.isChecked())
        self.close()
