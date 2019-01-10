from PyQt5 import QtWidgets, QtGui
import CodeArea
import DebugArea
import ControlBar
import Stack
import SymTable
import Interpreter


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(None)
        self.setWindowTitle("X0 Rush")
        self.setWindowIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DesktopIcon))

        font = QtGui.QFont()
        font.setFamily("Computer Modern")
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.messageArea = QtWidgets.QPlainTextEdit(self)
        self.messageArea.setReadOnly(True)
        self.messageArea.setFont(font)
        self.messageArea.appendPlainText("> Zihan Liu's in his heaven, all's right with the world.\n")
        self.interpreter = Interpreter.Interpreter(self)

        self.controlBar = ControlBar.ControlBar(self)
        self.codeArea = CodeArea.CodeArea(self)

        self.debugArea = DebugArea.DebugArea(self)
        self.stack = Stack.Stack(self)
        self.symTable = SymTable.SymTable(self)

        self.mainHLayout = QtWidgets.QHBoxLayout(self)
        self.mainHLayout.addLayout(self.controlBar)
        codeVLayout = QtWidgets.QVBoxLayout()
        codeVLayout.addWidget(self.codeArea, 70)
        codeVLayout.addWidget(self.messageArea, 30)
        self.mainHLayout.addLayout(codeVLayout)
        debugHLayout = QtWidgets.QHBoxLayout()
        debugVLayout = QtWidgets.QVBoxLayout()
        debugHLayout.addWidget(self.debugArea)
        debugHLayout.addWidget(self.stack)
        debugVLayout.addLayout(debugHLayout)
        debugVLayout.addWidget(self.symTable)
        self.mainHLayout.addLayout(debugVLayout)

        self.debugArea.hide()
        self.symTable.hide()
        self.stack.hide()

    def executeMode(self):
        self.debugArea.show()
        self.symTable.hide()
        self.stack.hide()
        self.debugArea.enableBreakpoints(False)
        for btn in self.controlBar.debugButtons:
            btn.setDisabled(True)
        self.debugArea.readFile('./inter_code')
        self.interpreter.init('./inter_code')
        self.stack.init()
        self.interpreter.execute()

    def debugMode(self):
        self.debugArea.show()
        self.symTable.show()
        self.stack.show()
        self.debugArea.enableBreakpoints(True)
        for btn in self.controlBar.debugButtons:
            btn.setEnabled(True)
        self.debugArea.readFile('./inter_code')
        self.symTable.readFile('./sym_table')
        self.interpreter.init('./inter_code')
        self.stack.init()
