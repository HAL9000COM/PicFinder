# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.actionPreference = QAction(MainWindow)
        self.actionPreference.setObjectName(u"actionPreference")
        self.actionClear_DB = QAction(MainWindow)
        self.actionClear_DB.setObjectName(u"actionClear_DB")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.lineEdit_folder = QLineEdit(self.centralwidget)
        self.lineEdit_folder.setObjectName(u"lineEdit_folder")

        self.horizontalLayout.addWidget(self.lineEdit_folder)

        self.pushButton_folder_browse = QPushButton(self.centralwidget)
        self.pushButton_folder_browse.setObjectName(u"pushButton_folder_browse")

        self.horizontalLayout.addWidget(self.pushButton_folder_browse)

        self.pushButton_index = QPushButton(self.centralwidget)
        self.pushButton_index.setObjectName(u"pushButton_index")

        self.horizontalLayout.addWidget(self.pushButton_index)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.lineEdit_search = QLineEdit(self.centralwidget)
        self.lineEdit_search.setObjectName(u"lineEdit_search")

        self.horizontalLayout_2.addWidget(self.lineEdit_search)

        self.pushButton_search = QPushButton(self.centralwidget)
        self.pushButton_search.setObjectName(u"pushButton_search")

        self.horizontalLayout_2.addWidget(self.pushButton_search)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.listWidget_search_result = QListWidget(self.widget)
        self.listWidget_search_result.setObjectName(u"listWidget_search_result")

        self.verticalLayout_2.addWidget(self.listWidget_search_result)


        self.verticalLayout.addWidget(self.widget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuFile.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionClear_DB)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"PicFinder", None))
        self.actionPreference.setText(QCoreApplication.translate("MainWindow", u"Preference", None))
        self.actionClear_DB.setText(QCoreApplication.translate("MainWindow", u"Clear Database", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Folder:", None))
        self.pushButton_folder_browse.setText(QCoreApplication.translate("MainWindow", u"Browse", None))
        self.pushButton_index.setText(QCoreApplication.translate("MainWindow", u"Index", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Search:", None))
        self.pushButton_search.setText(QCoreApplication.translate("MainWindow", u"Search", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
    # retranslateUi

