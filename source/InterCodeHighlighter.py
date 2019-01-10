from PyQt5 import QtGui, QtCore


class InterCodeHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.highlightingRules = []

        keywordFormat = QtGui.QTextCharFormat()
        keywordFormat.setForeground(QtGui.QColor(104, 151, 187))
        keywordFormat.setFontWeight(QtGui.QFont.Bold)
        keywords = ["lit", "sto", "lod"]
        for word in keywords:
            pattern = QtCore.QRegExp("\\b" + word + "\\b")
            rule = (pattern, keywordFormat)
            self.highlightingRules.append(rule)

        keywords = ["cal", "ini"]
        keywordFormat1 = QtGui.QTextCharFormat()
        keywordFormat1.setForeground(QtGui.QColor(220, 220, 170))
        keywordFormat1.setFontWeight(QtGui.QFont.Bold)
        for word in keywords:
            pattern = QtCore.QRegExp("\\b" + word + "\\b")
            rule = (pattern, keywordFormat1)
            self.highlightingRules.append(rule)

        keywords = ["jmp", "jpc"]
        keywordFormat2 = QtGui.QTextCharFormat()
        keywordFormat2.setForeground(QtGui.QColor(195, 124, 69))
        keywordFormat2.setFontWeight(QtGui.QFont.Bold)
        for word in keywords:
            pattern = QtCore.QRegExp("\\b" + word + "\\b")
            rule = (pattern, keywordFormat2)
            self.highlightingRules.append(rule)

        keywords = ["opr"]
        keywordFormat3 = QtGui.QTextCharFormat()
        keywordFormat3.setForeground(QtGui.QColor(130, 78, 92))
        keywordFormat3.setFontWeight(QtGui.QFont.Bold)
        for word in keywords:
            pattern = QtCore.QRegExp("\\b" + word + "\\b")
            rule = (pattern, keywordFormat3)
            self.highlightingRules.append(rule)

        numberFormat = QtGui.QTextCharFormat()
        numberFormat.setForeground(QtGui.QColor(181, 206, 168))
        self.highlightingRules.append((QtCore.QRegExp("\\b[0-9]+\\b"), numberFormat))

    def highlightBlock(self, text):
        for rule in self.highlightingRules:
            index = rule[0].indexIn(text)
            while index >= 0:
                length = rule[0].matchedLength()
                self.setFormat(index, length, rule[1])
                index = rule[0].indexIn(text, index + length)
        self.setCurrentBlockState(0)
