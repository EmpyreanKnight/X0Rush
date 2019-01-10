import re
from PyQt5 import QtWidgets, QtGui


class Interpreter:
    STACK_SIZE = 40960

    def __init__(self, parent):
        self.st = self.STACK_SIZE * [-1]
        self.pointer = 0
        self.base = 0
        self.top = 0
        self.instTable = []
        self.parent = parent
        self.status = 0

    def init(self, path):
        self.st = self.STACK_SIZE * [-1]
        self.pointer = 0
        self.top = -1
        self.base = 0
        self.status = 1
        self.instTable = [line.replace('  ', ' ').replace('\n', ' ').replace('\t', ' ')
                              .split(' ')[1:4] for line in open(path, "rt").readlines()]

    def interpret(self):
        if self.pointer >= len(self.instTable) or self.pointer < 0:
            self.parent.messageArea.appendPlainText('Displaced PC position, program forced exited!')
            self.status = 0
            return

        inst = self.instTable[self.pointer]
        inst[1] = int(inst[1])
        inst[2] = int(inst[2])
        self.pointer += 1

        if inst[0] == 'lit':
            self.top += 1
            self.st[self.top] = inst[2]
        elif inst[0] == 'opr':
            if inst[2] == 0:
                if inst[1] == 0:
                    self.top = self.base - 1
                    self.pointer = self.st[self.top + 3]
                    self.base = self.st[self.top + 2]
                else:
                    self.st[self.base] = self.st[self.top]
                    self.top = self.base
                    self.pointer = self.st[self.top + 2]
                    self.base = self.st[self.top + 1]
            elif inst[2] == 1:
                self.st[self.top] = -self.st[self.top]
            elif inst[2] == 2:
                self.top -= 1
                self.st[self.top] = self.st[self.top] + self.st[self.top + 1]
            elif inst[2] == 3:
                self.top -= 1
                self.st[self.top] = self.st[self.top] - self.st[self.top + 1]
            elif inst[2] == 4:
                self.top -= 1
                self.st[self.top] = self.st[self.top] * self.st[self.top + 1]
            elif inst[2] == 5:
                self.top -= 1
                self.st[self.top] = int(self.st[self.top] / self.st[self.top + 1])
            elif inst[2] == 6:
                self.st[self.top] = self.st[self.top] % 2
            elif inst[2] == 7:
                self.top -= 1
                self.st[self.top] = self.st[self.top] % self.st[self.top + 1]
            elif inst[2] == 8:
                self.top -= 1
                self.st[self.top] = int(self.st[self.top] == self.st[self.top + 1])
            elif inst[2] == 9:
                self.top -= 1
                self.st[self.top] = int(self.st[self.top] != self.st[self.top + 1])
            elif inst[2] == 10:
                self.top -= 1
                self.st[self.top] = int(self.st[self.top] < self.st[self.top + 1])
            elif inst[2] == 11:
                self.top -= 1
                self.st[self.top] = int(self.st[self.top] >= self.st[self.top + 1])
            elif inst[2] == 12:
                self.top -= 1
                self.st[self.top] = int(self.st[self.top] <= self.st[self.top + 1])
            elif inst[2] == 13:
                self.top -= 1
                self.st[self.top] = int(self.st[self.top] > self.st[self.top + 1])
            elif inst[2] == 14:
                if inst[1] == 1:
                    self.insertText(str(bool(self.st[self.top])))
                elif inst[1] == 2:
                    try:
                        c = chr(self.st[self.top])
                    except:
                        c = ' '
                    self.insertText(c)
                elif inst[1] == 3:
                    self.insertText(str(self.st[self.top]))
                self.top -= 1
            elif inst[2] == 15:
                self.insertText('\n')
            elif inst[2] == 16:
                self.top += 1
                if inst[1] == 1:
                    b = self.getInput('Please enter a bool value:')
                    if re.match(r"^[-+]?\d+$", b) is not None:
                        self.st[self.top] = int(bool(b))
                    elif b.lower() == 'true':
                        self.st[self.top] = 1
                    elif b.lower() == 'false':
                        self.st[self.top] = 0
                    else:
                        self.parent.messageArea.appendPlainText('Invalid input, use false instead')
                        self.st[self.top] = 0
                elif inst[1] == 2:
                    c = self.getInput('Please enter a character:')
                    self.st[self.top] = int(c[0])
                else:
                    i = self.getInput('Please input an integer:')
                    if re.match(r"^[-+]?\d+$", i) is not None:
                        self.st[self.top] = int(i)
                    else:
                        self.parent.messageArea.appendPlainText('Invalid input, use 0 instead')
                        self.st[self.top] = 0
            elif inst[2] == 17:
                self.st[self.top] = int(not self.st[self.top])
            elif inst[2] == 18:
                self.top -= 1
                self.st[self.top] = int(self.st[self.top] and self.st[self.top + 1])
            elif inst[2] == 19:
                self.top -= 1
                self.st[self.top] = int(self.st[self.top] or self.st[self.top + 1])
            elif inst[2] == 20:  # xor
                self.top -= 1
                self.st[self.top] = int(bool(self.st[self.top]) != bool(self.st[self.top + 1]))
            elif inst[2] == 21:
                self.st[self.top] = (self.st[self.top] == self.st[self.top - 1])
            elif inst[2] == 22:
                self.top -= 1
            elif inst[2] == 23:
                self.top += 1
                self.st[self.top] = self.st[self.top - 1]
            elif inst[2] == 24:
                if inst[1] == 1:
                    self.st[self.top + 3] = int(bool(self.st[self.top]))
                else:
                    self.st[self.top + 3] = self.st[self.top]
                self.top -= 1
            elif inst[2] == 25:  # type conversion
                if inst[1] == 1:
                    self.st[self.top] = int(bool(self.st[self.top]))
                else:
                    self.st[self.top] = self.st[self.top]
        elif inst[0] == 'lod':
            if inst[1] >= 0:
                self.top += 1
                self.st[self.top] = self.st[self.get_base(inst[1]) + inst[2]]
            else:
                self.st[self.top] = self.st[self.get_base(-inst[1] - 1) + inst[2] + self.st[self.top]]
        elif inst[0] == 'sto':
            if inst[1] >= 0:
                self.st[self.get_base(inst[1]) + inst[2]] = self.st[self.top]
            else:
                self.st[self.get_base(-inst[1] - 1) + inst[2] + self.st[self.top - 1]] = self.st[self.top]
                self.st[self.top - 1] = self.st[self.top]
                self.top -= 1
        elif inst[0] == 'cal':
            if inst[1] == -1:
                self.st[self.top + 1] = 0
                self.st[self.top + 2] = 0
                self.st[self.top + 3] = 0
            else:
                self.st[self.top + 1] = self.get_base(inst[1])
                self.st[self.top + 2] = self.base
                self.st[self.top + 3] = self.pointer
            self.base = self.top + 1
            self.pointer = inst[2]
        elif inst[0] == 'ini':
            self.top += inst[2]
        elif inst[0] == 'jmp':
            self.pointer = inst[2]
        elif inst[0] == 'jpc':
            if self.st[self.top] == 0:
                self.pointer = inst[2]
            self.top -= 1

        if self.pointer == 0:
            self.status = 0
            self.insertText("Program exited.\n")

        if self.top >= self.STACK_SIZE or self.top < -1:
            self.parent.messageArea.appendPlainText('Stack overflow, program forced exited!')
            self.status = 0

    def step(self):
        if self.status != 0:
            self.interpret()
            self.parent.stack.updateData(self.st, self.top + 1)
            self.parent.debugArea.movePointer(self.pointer)

    def toBreakpoint(self):
        breakpoints = self.parent.debugArea.breakpoints
        self.interpret()
        while self.status != 0 and self.pointer not in breakpoints:
            self.interpret()
        self.parent.stack.updateData(self.st, self.top + 1)
        self.parent.debugArea.movePointer(self.pointer)

    def execute(self):
        while self.status != 0:
            self.interpret()

    def get_base(self, level):
        old_base = self.base
        while level > 0:
            old_base = self.st[old_base]
            level -= 1
        return old_base

    def getInput(self, prompt):
        ret = QtWidgets.QInputDialog.getText(self.parent, 'Input Dialog', prompt)
        return ret[0]

    def insertText(self, text):
        self.parent.messageArea.moveCursor(QtGui.QTextCursor.End)
        self.parent.messageArea.insertPlainText(text)
