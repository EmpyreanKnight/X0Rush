# -*- coding: utf-8 -*-

import sys
import MainWindow
from PyQt5 import QtWidgets, QtGui, QtCore


def setTheme(app):
    app.setStyle('Fusion')
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(30, 30, 30))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(14, 99, 156).lighter())
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(palette)


def setSizeAndCenter(window, width, height):
    size = window.rect()
    size.setSize(QtCore.QSize(width, height))
    xCoord = QtWidgets.QApplication.desktop().screen().rect().center().x() - size.center().x()
    yCoord = QtWidgets.QApplication.desktop().screen().rect().center().y() - size.center().y()
    window.setGeometry(xCoord, yCoord, width, height)


def main():
    app = QtWidgets.QApplication(sys.argv)
    setTheme(app)
    window = MainWindow.MainWindow()
    setSizeAndCenter(window, 1366, 768)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
