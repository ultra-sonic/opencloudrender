# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ocrSubmit.ui'
#
# Created: Fri Mar 27 09:06:58 2015
#      by: pyside-uic 0.2.14 running on PySide 1.2.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_OpenCloudRenderSubmit(object):
    def setupUi(self, OpenCloudRenderSubmit):
        OpenCloudRenderSubmit.setObjectName("OpenCloudRenderSubmit")
        OpenCloudRenderSubmit.resize(1400, 300)
        OpenCloudRenderSubmit.setAcceptDrops(True)
        self.centralwidget = QtGui.QWidget(OpenCloudRenderSubmit)
        self.centralwidget.setObjectName("centralwidget")
        self.scenesTableView = QtGui.QTableView(self.centralwidget)
        self.scenesTableView.setGeometry(QtCore.QRect(40, 20, 1161, 170))
        self.scenesTableView.setAcceptDrops(True)
        self.scenesTableView.setObjectName("scenesTableView")
        self.syncAssetsAndSubmitButton = QtGui.QPushButton(self.centralwidget)
        self.syncAssetsAndSubmitButton.setGeometry(QtCore.QRect(1210, 120, 171, 32))
        self.syncAssetsAndSubmitButton.setObjectName("syncAssetsAndSubmitButton")
        self.syncAssetsButton = QtGui.QPushButton(self.centralwidget)
        self.syncAssetsButton.setGeometry(QtCore.QRect(1210, 80, 171, 32))
        self.syncAssetsButton.setObjectName("syncAssetsButton")
        self.syncImagesButton = QtGui.QPushButton(self.centralwidget)
        self.syncImagesButton.setGeometry(QtCore.QRect(1210, 160, 171, 32))
        self.syncImagesButton.setObjectName("syncImagesButton")
        self.addScenesButton = QtGui.QPushButton(self.centralwidget)
        self.addScenesButton.setEnabled(False)
        self.addScenesButton.setGeometry(QtCore.QRect(1210, 20, 171, 32))
        self.addScenesButton.setObjectName("addScenesButton")
        self.dataBucketName = QtGui.QLineEdit(self.centralwidget)
        self.dataBucketName.setGeometry(QtCore.QRect(140, 230, 431, 20))
        self.dataBucketName.setObjectName("dataBucketName")
        self.repoBucketName = QtGui.QLineEdit(self.centralwidget)
        self.repoBucketName.setGeometry(QtCore.QRect(770, 230, 431, 20))
        self.repoBucketName.setObjectName("repoBucketName")
        self.uploadProgressBar = QtGui.QProgressBar(self.centralwidget)
        self.uploadProgressBar.setGeometry(QtCore.QRect(40, 200, 1331, 23))
        self.uploadProgressBar.setProperty("value", 0)
        self.uploadProgressBar.setObjectName("uploadProgressBar")
        self.dataBucketNameLabel = QtGui.QLabel(self.centralwidget)
        self.dataBucketNameLabel.setGeometry(QtCore.QRect(41, 230, 100, 20))
        self.dataBucketNameLabel.setObjectName("dataBucketNameLabel")
        self.repoBucketNameLabel = QtGui.QLabel(self.centralwidget)
        self.repoBucketNameLabel.setGeometry(QtCore.QRect(630, 230, 140, 20))
        self.repoBucketNameLabel.setObjectName("repoBucketNameLabel")
        self.dragDropOnlyLabel = QtGui.QLabel(self.centralwidget)
        self.dragDropOnlyLabel.setGeometry(QtCore.QRect(1220, 50, 151, 20))
        self.dragDropOnlyLabel.setObjectName("dragDropOnlyLabel")
        OpenCloudRenderSubmit.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1400, 22))
        self.menubar.setObjectName("menubar")
        OpenCloudRenderSubmit.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(OpenCloudRenderSubmit)
        self.statusbar.setObjectName("statusbar")
        OpenCloudRenderSubmit.setStatusBar(self.statusbar)

        self.retranslateUi(OpenCloudRenderSubmit)
        QtCore.QMetaObject.connectSlotsByName(OpenCloudRenderSubmit)

    def retranslateUi(self, OpenCloudRenderSubmit):
        OpenCloudRenderSubmit.setWindowTitle(QtGui.QApplication.translate("OpenCloudRenderSubmit", "OpenCloudRender", None, QtGui.QApplication.UnicodeUTF8))
        self.syncAssetsAndSubmitButton.setText(QtGui.QApplication.translate("OpenCloudRenderSubmit", "sync assets + submit", None, QtGui.QApplication.UnicodeUTF8))
        self.syncAssetsButton.setText(QtGui.QApplication.translate("OpenCloudRenderSubmit", "sync assets", None, QtGui.QApplication.UnicodeUTF8))
        self.syncImagesButton.setText(QtGui.QApplication.translate("OpenCloudRenderSubmit", "sync images", None, QtGui.QApplication.UnicodeUTF8))
        self.addScenesButton.setText(QtGui.QApplication.translate("OpenCloudRenderSubmit", "add .vrscene/.ass files", None, QtGui.QApplication.UnicodeUTF8))
        self.dataBucketNameLabel.setText(QtGui.QApplication.translate("OpenCloudRenderSubmit", "S3 Data Bucket", None, QtGui.QApplication.UnicodeUTF8))
        self.repoBucketNameLabel.setText(QtGui.QApplication.translate("OpenCloudRenderSubmit", "S3 Repository Bucket", None, QtGui.QApplication.UnicodeUTF8))
        self.dragDropOnlyLabel.setText(QtGui.QApplication.translate("OpenCloudRenderSubmit", "drag&drop only for now", None, QtGui.QApplication.UnicodeUTF8))

