import os

from PyQt5 import QtWidgets
from subprocess import PIPE, Popen


class ControlBar(QtWidgets.QVBoxLayout):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.fileName = None
        self.debugButtons = []

        button = QtWidgets.QPushButton(parent)
        button.setIcon(parent.style().standardIcon(QtWidgets.QStyle.SP_FileIcon))
        button.setToolTip("New File (Ctrl+N)")
        button.clicked.connect(self.onNew)
        button.setShortcut('Ctrl+N')
        self.addWidget(button)

        button = QtWidgets.QPushButton(parent)
        button.setIcon(parent.style().standardIcon(QtWidgets.QStyle.SP_DialogOpenButton))
        button.setToolTip("Open File (Ctrl+O)")
        button.clicked.connect(self.onLoad)
        button.setShortcut('Ctrl+O')
        self.addWidget(button)

        button = QtWidgets.QPushButton(parent)
        button.setIcon(parent.style().standardIcon(QtWidgets.QStyle.SP_DialogSaveButton))
        button.setToolTip("Save File (Ctrl+S)")
        button.clicked.connect(self.onSave)
        button.setShortcut('Ctrl+S')
        self.addWidget(button)

        button = QtWidgets.QPushButton(parent)
        button.setIcon(parent.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        button.setToolTip("Compile and Run (Ctrl+F5)")
        button.clicked.connect(self.onRun)
        button.setShortcut('Ctrl+F5')
        self.addWidget(button)

        button = QtWidgets.QPushButton(parent)
        button.setIcon(parent.style().standardIcon(QtWidgets.QStyle.SP_DialogNoButton))
        button.setToolTip("Compile and Debug (F5)")
        button.clicked.connect(self.onDebug)
        button.setShortcut('F5')
        self.addWidget(button)

        button = QtWidgets.QPushButton(parent)
        button.setIcon(parent.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekForward))
        button.setToolTip("Step Debug (F1)")
        button.clicked.connect(self.onStep)
        self.addWidget(button)
        button.setShortcut('F1')
        self.debugButtons.append(button)

        button = QtWidgets.QPushButton(parent)
        button.setIcon(parent.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipForward))
        button.setToolTip("To Next Breakpoint (F2)")
        button.clicked.connect(self.onNext)
        button.setShortcut('F2')
        self.addWidget(button)
        self.debugButtons.append(button)

        button = QtWidgets.QPushButton(parent)
        button.setIcon(parent.style().standardIcon(QtWidgets.QStyle.SP_MediaStop))
        button.setToolTip("End Debug (F3)")
        button.clicked.connect(self.onStop)
        button.setShortcut('F3')
        self.addWidget(button)
        self.debugButtons.append(button)

    def onNew(self):
        self.parent.codeArea.clear()
        self.fileName = None

    def onLoad(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self.parent, 'Add X0 Source', './', "X0 File (*.txt *.x0)")
        if fileName[0]:
            self.fileName = fileName[0]
            self.parent.codeArea.clear()
            self.parent.codeArea.setPlainText(open(fileName[0]).read())

    def onSave(self):
        if not self.fileName:
            fileName = QtWidgets.QFileDialog.getSaveFileName(self.parent, 'Save File')
            if fileName[0]:
                self.fileName = fileName[0]
            else:
                return

        if not self.fileName.endswith(".x0"):
            self.fileName += ".x0"

        with open(self.fileName, "wt") as file:
            file.write(self.parent.codeArea.toPlainText())

    def onRun(self):
        self.onSave()
        if not self.fileName:
            return
        if not os.path.isfile(os.getcwd() + '\\x0.exe'):
            self.parent.messageArea.appendPlainText('Compiler not found, mission abort.\n')
            return
        p = Popen(os.getcwd() + '\\x0.exe ' + self.fileName, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout, stderr = p.communicate()
        if "error" not in str(stderr):
            self.parent.messageArea.appendPlainText(stdout.decode("utf-8"))
            self.parent.messageArea.appendPlainText('Executing program...\n')
            self.parent.executeMode()
        else:
            self.parent.messageArea.appendPlainText(stderr.decode("utf-8"))
            self.parent.messageArea.appendPlainText('Compile failed...\n')

    def onDebug(self):
        self.onSave()
        if not self.fileName:
            return
        if not os.path.isfile(os.getcwd() + '\\x0.exe'):
            self.parent.messageArea.appendPlainText('Compiler not found, mission abort.\n')
            return
        p = Popen(os.getcwd() + '\\x0.exe ' + self.fileName, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout, stderr = p.communicate()
        if "error" not in str(stderr):
            self.parent.messageArea.appendPlainText(stdout.decode("utf-8"))
            self.parent.messageArea.appendPlainText('Initiate debug process...\n')
            self.parent.debugMode()
        else:
            self.parent.messageArea.appendPlainText(stderr.decode("utf-8"))
            self.parent.messageArea.appendPlainText('Compile failed...\n')

    def onStep(self):
        self.parent.interpreter.step()

    def onNext(self):
        self.parent.interpreter.toBreakpoint()

    def onStop(self):
        if self.parent.stack.isVisible():
            self.parent.executeMode()
        else:
            self.parent.debugArea.hide()
