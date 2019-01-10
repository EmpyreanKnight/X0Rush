from PyQt5 import QtWidgets


class SymTable(QtWidgets.QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setRowCount(0)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(['ID', 'TYPE', 'MODIFIER', 'ADDR', 'SIZE', 'LEVEL', 'COMMENT'])
        self.data = []

    def readFile(self, path):
        self.data = self.fetchSymTable(path)
        self.setRowCount(len(self.data))
        for i in range(0, len(self.data)):
            for j in range(0, len(self.data[i])):
                self.setItem(i, j, QtWidgets.QTableWidgetItem(self.data[i][j]))
        self.resizeColumnsToContents()

    @staticmethod
    def fetchSymTable(path):
        lines = open(path, "rt").readlines()
        data = []
        for line in lines:
            data.append(line.split(' '))
        return data
