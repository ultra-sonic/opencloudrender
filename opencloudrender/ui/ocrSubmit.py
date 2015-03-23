# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ocrSubmit.ui'
#
# Created: Mon Mar 23 19:28:48 2015
#      by: pyside-uic 0.2.14 running on PySide 1.2.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(987, 332)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.vrscenesTableView = QtGui.QTableView(self.centralwidget)
        self.vrscenesTableView.setGeometry(QtCore.QRect(40, 60, 911, 171))
        self.vrscenesTableView.setAcceptDrops(True)
        self.vrscenesTableView.setObjectName("vrscenesTableView")
        self.syncAssetsAndSubmitButton = QtGui.QPushButton(self.centralwidget)
        self.syncAssetsAndSubmitButton.setGeometry(QtCore.QRect(400, 250, 171, 32))
        self.syncAssetsAndSubmitButton.setObjectName("syncAssetsAndSubmitButton")
        self.syncAssetsButton = QtGui.QPushButton(self.centralwidget)
        self.syncAssetsButton.setGeometry(QtCore.QRect(40, 250, 111, 32))
        self.syncAssetsButton.setObjectName("syncAssetsButton")
        self.syncImagesButton = QtGui.QPushButton(self.centralwidget)
        self.syncImagesButton.setGeometry(QtCore.QRect(810, 250, 114, 32))
        self.syncImagesButton.setObjectName("syncImagesButton")
        self.addVrscenesButton = QtGui.QPushButton(self.centralwidget)
        self.addVrscenesButton.setGeometry(QtCore.QRect(410, 20, 151, 32))
        self.addVrscenesButton.setObjectName("addVrscenesButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0, 0, 987, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.syncAssetsAndSubmitButton.setText(QtGui.QApplication.translate("MainWindow", "sync assets + submit", None, QtGui.QApplication.UnicodeUTF8))
        self.syncAssetsButton.setText(QtGui.QApplication.translate("MainWindow", "sync assets", None, QtGui.QApplication.UnicodeUTF8))
        self.syncImagesButton.setText(QtGui.QApplication.translate("MainWindow", "sync images", None, QtGui.QApplication.UnicodeUTF8))
        self.addVrscenesButton.setText(QtGui.QApplication.translate("MainWindow", "add .vrscene files", None, QtGui.QApplication.UnicodeUTF8))

