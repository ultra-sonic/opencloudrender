from PySide import QtGui,QtCore
import os
import ocrSubmit
import operator
from opencloudrender.vraySceneSync import uploadWithDependencies
from opencloudrender.vray_utils import get_vrscene_data_tuple

#todo redirect stdout to a log textfield

class ControlMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)

        #todo implement this as an .openclouderender json file
        self.repo_bucket_name = os.environ.get( 'VRAY_REPO_BUCKET' , 'vray-repo' )
        self.data_bucket_name = os.environ.get( 'DATA_BUCKET'      , 'fbcloudrender-testdata' )


        self.header = [ 'scene', 'start', 'end', 'camera' , 'path' ]
        self.data_list = []
        self.table_model = ScenesTableModel(self, self.data_list, self.header) #maybe skip passing of data_list and header and use parent.data_list in ScenesTableModel

        self.ui =  ocrSubmit.Ui_OpenCloudRenderSubmit()
        self.ui.setupUi(self)
        self.ui.scenesTableView.setModel( self.table_model )
        self.ui.syncAssetsButton.clicked.connect( self.syncAssets )

    def syncAssets(self):
        for scene in self.data_list:
            uploadWithDependencies( self.data_bucket_name , scene[4] )

    def dragEnterEvent(self, e):

        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        pathList=e.mimeData().urls()
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        for url in pathList:
            path=url.toLocalFile()
            if os.path.isfile(path) and path.endswith('.vrscene'):
                vrscene_data = get_vrscene_data_tuple( path )
                self.table_model.add( vrscene_data  )
            #todo implement folder handling here
        self.emit(QtCore.SIGNAL("layoutChanged()"))

class ScenesTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, mylist, header, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header
    def add( self , vrscene_data ):
        if vrscene_data not in self.mylist:
            self.mylist.append( vrscene_data )
            self.sort( 0 , QtCore.Qt.AscendingOrder )

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
        elif role != QtCore.Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.mylist = sorted(self.mylist,
            key=operator.itemgetter(col))
        if order == QtCore.Qt.DescendingOrder:
            self.mylist.reverse()
        self.emit(QtCore.SIGNAL("layoutChanged()"))