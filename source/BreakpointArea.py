from PyQt5 import QtWidgets, QtCore


class BreakpointArea(QtWidgets.QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QtCore.QSize(self.editor.WIDTH, 0)

    def paintEvent(self, event):
        self.editor.breakpointAreaPaintEvent(event)

    def mouseReleaseEvent(self, QMouseEvent):
        self.editor.toggleBreakpoint(QMouseEvent)

