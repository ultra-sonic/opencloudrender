''' ps_QAbstractTableModel_solvents.py
use PySide's QTableView and QAbstractTableModel for tabular data
sort columns by clicking on the header title

here applied to solvents commonly used in Chemistry

PySide is the official LGPL-licensed version of PyQT
tested with PySide112 and Python27/Python33 by vegaseat  15feb2013
'''

import operator
from PySide.QtCore import *
from PySide.QtGui import *
from vray_utils import get_vrscene_data_tuple


class MyWindow(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        # setGeometry(x_pos, y_pos, width, height)
        header = [ 'vrscene', 'start', 'end', 'camera']
        data_list = []

        self.setGeometry(300, 200, 600, 450)
        self.setWindowTitle("Click on column title to sort")

        self.table_model = MyTableModel(self, data_list, header)
        table_view = QTableView()
        table_view.setModel(self.table_model)
        # set font
        font = QFont("Courier New", 14)
        table_view.setFont(font)
        # set column width to fit contents (set font first!)
        table_view.resizeColumnsToContents()
        # enable sorting
        table_view.setSortingEnabled(True)
        #table_view.setDragEnabled(True)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.addWidget(table_view)
        self.setLayout(layout)

    def dragEnterEvent(self, e):

        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.accept()

    def dropEvent(self, e):
        pathList=e.mimeData().urls()
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        for url in pathList:
            path=url.toLocalFile()
            if path.endswith('.vrscene'):
                vrscene_data = get_vrscene_data_tuple( path )
                self.table_model.add( vrscene_data  )
        self.emit(SIGNAL("layoutChanged()"))


class MyTableModel(QAbstractTableModel):
    def __init__(self, parent, mylist, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header
    def add( self , vrscene_data ):
        self.mylist.append( vrscene_data )
        self.sort( 0 , Qt.AscendingOrder )

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        if len(self.mylist):
            return len(self.mylist[0])
        else:
            return 0

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.mylist = sorted(self.mylist,
            key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.mylist.reverse()
        self.emit(SIGNAL("layoutChanged()"))