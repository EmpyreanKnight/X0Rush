from PyQt5 import QtWidgets, QtGui, QtCore
import BreakpointArea
import InterCodeHighlighter


class DebugArea(QtWidgets.QPlainTextEdit):
    WIDTH = 20

    def __init__(self, parent):
        super().__init__(parent)
        self.breakpointArea = BreakpointArea.BreakpointArea(self)
        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setFixedPitch(True)
        font.setPointSize(12)
        self.setFont(font)
        self.setReadOnly(True)
        self.enable = False

        self.highlighter = InterCodeHighlighter.InterCodeHighlighter(self.document())
        self.setViewportMargins(self.WIDTH, 0, 0, 0)

        self.updateRequest.connect(self.updateBreakpointArea)

        self.breakpoints = []
        self.HEIGHT = self.blockBoundingRect(self.firstVisibleBlock()).height()

    def readFile(self, path):
        self.setPlainText(open(path, "rt").read())
        self.resetPointer()

    def toggleBreakpoint(self, event):
        if not self.enable:
            return
        cur = self.cursorForPosition(event.pos())
        pos = cur.blockNumber()
        if pos in self.breakpoints:
            self.breakpoints.remove(pos)
        else:
            self.breakpoints.append(pos)
        self.breakpointArea.repaint()

    def updateBreakpointArea(self, rect, dy):
        if dy:
            self.breakpointArea.scroll(0, dy)
        else:
            self.breakpointArea.update(0, rect.y(), self.breakpointArea.width(),
                                       rect.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.breakpointArea.setGeometry(QtCore.QRect(cr.left(), cr.top(),
                                        self.WIDTH, cr.height()))

    def breakpointAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self.breakpointArea)
        painter.fillRect(event.rect(), QtGui.QColor(40, 40, 40))

        if not self.enable:
            return

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        height = self.blockBoundingRect(block).height()
        bottom = top + height
        self.HEIGHT = height

        painter.setBrush(QtCore.Qt.red)
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                if blockNumber in self.breakpoints:
                    painter.drawEllipse(QtCore.QPointF(self.WIDTH/2, top+height/2), 5, 5)

            block = block.next()
            top = bottom
            height = self.blockBoundingRect(block).height()
            bottom = top + height
            blockNumber += 1

    def resetPointer(self):
        extraSelections = []
        selection = QtWidgets.QTextEdit.ExtraSelection()
        lineColor = QtGui.QColor(QtGui.QColor(QtCore.Qt.darkRed))
        selection.format.setBackground(lineColor)
        selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)

        selection.cursor = self.textCursor()
        selection.cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
        selection.cursor.clearSelection()
        extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def movePointer(self, index):
        extraSelections = []
        selection = QtWidgets.QTextEdit.ExtraSelection()
        lineColor = QtGui.QColor(QtGui.QColor(QtCore.Qt.darkRed))
        selection.format.setBackground(lineColor)
        selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)

        selection.cursor = self.textCursor()
        selection.cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
        selection.cursor.movePosition(QtGui.QTextCursor.Down, QtGui.QTextCursor.MoveAnchor, index)
        selection.cursor.clearSelection()
        extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def enableBreakpoints(self, status):
        self.enable = status
        if not status:
            self.breakpoints = []

