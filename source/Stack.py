from PyQt5 import QtWidgets


class Stack(QtWidgets.QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setRowCount(0)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(['INDEX', 'VALUE'])
        self.verticalHeader().setVisible(False)

    def init(self):
        self.setRowCount(0)

    def updateData(self, data, size):
        self.clear()
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(['INDEX', 'VALUE'])
        self.setRowCount(size)
        for i in range(size):
            self.setItem(i, 0, QtWidgets.QTableWidgetItem(str(i)))
            self.setItem(i, 1, QtWidgets.QTableWidgetItem(str(data[i])))



