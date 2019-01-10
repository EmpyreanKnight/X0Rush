from PyQt5 import QtGui, QtCore


class X0Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.highlightingRules = []

        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtGui.QColor(86, 156, 214))
        keywordFormat.setFontWeight(QtGui.QFont.Bold)
        keywords = ["int", "char", "bool", "main", "if", "else", "while",
                    "read", "write", "const", "for", "do", "repeat", "until",
                    "switch", "case", "default", "return", "break", "continue",
                    "exit", "true", "false", "void"]
        for word in keywords:
            pattern = QtCore.QRegExp("\\b" + word + "\\b")
            rule = (pattern, keywordFormat)
            self.highlightingRules.append(rule)

        quotationFormat = QtGui.QTextCharFormat()
        quotationFormat.setForeground(QtGui.QColor(206, 145, 120))
        self.highlightingRules.append((QtCore.QRegExp("\".*\""), quotationFormat))

        numberFormat = QtGui.QTextCharFormat()
        numberFormat.setForeground(QtGui.QColor(181, 206, 168))
        self.highlightingRules.append((QtCore.QRegExp("\\b[0-9]+\\b"), numberFormat))

        singleLineCommentFormat = QtGui.QTextCharFormat()
        singleLineCommentFormat.setForeground(QtGui.QColor(106, 153, 85))
        self.highlightingRules.append((QtCore.QRegExp("//[^\n]*"), singleLineCommentFormat))

        self.multiLineCommentFormat = QtGui.QTextCharFormat()
        self.multiLineCommentFormat.setForeground(QtGui.QColor(106, 153, 85))
        self.commentStartExpression = QtCore.QRegExp("/\\*")
        self.commentEndExpression = QtCore.QRegExp("\\*/")

    def highlightBlock(self, text):
        for rule in self.highlightingRules:
            index = rule[0].indexIn(text)
            while index >= 0:
                length = rule[0].matchedLength()
                self.setFormat(index, length, rule[1])
                index = rule[0].indexIn(text, index + length)
        self.setCurrentBlockState(0)

        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)

        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()
            self.setFormat(startIndex, commentLength, self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text, startIndex + commentLength)
