# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/mnt/hgfs/Developpement/Debian_Dev/Eclipse/Workspace/BoardSimu/src/hardware/device/ledUI.ui'
#
# Created: Sun Apr 27 11:24:22 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ledWidget(object):
    def setupUi(self, ledWidget):
        ledWidget.setObjectName(_fromUtf8("ledWidget"))
        ledWidget.resize(647, 206)
        self.horizontalLayoutWidget = QtGui.QWidget(ledWidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 270, 31))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.decAddr = QtGui.QLabel(self.horizontalLayoutWidget)
        self.decAddr.setMinimumSize(QtCore.QSize(60, 0))
        self.decAddr.setMaximumSize(QtCore.QSize(60, 20))
        self.decAddr.setText(_fromUtf8(""))
        self.decAddr.setAlignment(QtCore.Qt.AlignCenter)
        self.decAddr.setObjectName(_fromUtf8("decAddr"))
        self.horizontalLayout.addWidget(self.decAddr)
        self.hexaAddr = QtGui.QLabel(self.horizontalLayoutWidget)
        self.hexaAddr.setMinimumSize(QtCore.QSize(60, 0))
        self.hexaAddr.setMaximumSize(QtCore.QSize(60, 20))
        self.hexaAddr.setText(_fromUtf8(""))
        self.hexaAddr.setAlignment(QtCore.Qt.AlignCenter)
        self.hexaAddr.setObjectName(_fromUtf8("hexaAddr"))
        self.horizontalLayout.addWidget(self.hexaAddr)
        self.label = QtGui.QLabel(self.horizontalLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.decValue = QtGui.QLabel(self.horizontalLayoutWidget)
        self.decValue.setMinimumSize(QtCore.QSize(60, 0))
        self.decValue.setMaximumSize(QtCore.QSize(60, 20))
        self.decValue.setText(_fromUtf8(""))
        self.decValue.setAlignment(QtCore.Qt.AlignCenter)
        self.decValue.setObjectName(_fromUtf8("decValue"))
        self.horizontalLayout.addWidget(self.decValue)
        self.hexaValue = QtGui.QLabel(self.horizontalLayoutWidget)
        self.hexaValue.setMinimumSize(QtCore.QSize(60, 0))
        self.hexaValue.setMaximumSize(QtCore.QSize(60, 20))
        self.hexaValue.setText(_fromUtf8(""))
        self.hexaValue.setAlignment(QtCore.Qt.AlignCenter)
        self.hexaValue.setObjectName(_fromUtf8("hexaValue"))
        self.horizontalLayout.addWidget(self.hexaValue)

        self.retranslateUi(ledWidget)
        QtCore.QMetaObject.connectSlotsByName(ledWidget)

    def retranslateUi(self, ledWidget):
        ledWidget.setWindowTitle(QtGui.QApplication.translate("ledWidget", "LED", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ledWidget", ":", None, QtGui.QApplication.UnicodeUTF8))

