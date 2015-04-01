from PySide import QtGui,QtCore
import os
import ocrSubmit
import operator
import opencloudrender
from opencloudrender.afanasySubmit import sendJob
from opencloudrender.vraySceneSync import uploadWithDependencies
from opencloudrender.vray_utils    import get_vrscene_data_tuple

#todo redirect stdout to a log textfield

class ControlMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)

        self.header = [ 'scenepath', 'start', 'end', 'camera' ]
        self.data_list = []
        self.table_model = ScenesTableModel(self, self.data_list, self.header) #maybe skip passing of data_list and header and use parent.data_list in ScenesTableModel

        self.ui =  ocrSubmit.Ui_OpenCloudRenderSubmit()
        self.ui.setupUi(self)

        #Table
        self.ui.scenesTableView.setModel( self.table_model )

        #Buttons
        self.ui.syncAssetsButton.clicked.connect( self.syncAssets )
        self.ui.syncAssetsAndSubmitButton.clicked.connect( self.syncAssetsAndSubmit )
        self.ui.syncImagesButton.clicked.connect( self.syncImages )

        #Buckets
        self.ui.dataBucketName.setText( os.environ.get( 'DATA_BUCKET'      , 'fbcloudrender-testdata' ) ) #todo implement this as an .openclouderender json file
        self.ui.repoBucketName.setText( os.environ.get( 'VRAY_REPO_BUCKET' , 'vray-repo' ) )

        #Dropdown
        self.ui.vrayVersionComboBox.addItem('30001')
        self.ui.vrayVersionComboBox.addItem('24002')

    def syncAssets(self):
        self.ui.uploadProgressBar.setValue(0) # todo - add cancel button

        for scene in self.data_list:
            if uploadWithDependencies( self.ui.dataBucketName.text() , scene[0] , progress_bar=self.ui.uploadProgressBar ) != 0:
                print 'ERROR: some assets could not be uploaded!'

    def syncAssetsAndSubmit(self):
        self.ui.uploadProgressBar.setValue(0)

        for scene in self.data_list:
            if uploadWithDependencies( self.ui.dataBucketName.text() , scene[0] , progress_bar=self.ui.uploadProgressBar ) != 0:
                print 'ERROR: some assets could not be uploaded! SUBMITTING ANYWAY FOR NOW - beta phase!'  #todo do not submit at final release! uncomment next line
                #raise "Aborting!"
            sendJob( scene[0] , priority=50 , vray_build=self.ui.vrayVersionComboBox.currentText() )

    def syncImages(self):
        self.ui.uploadProgressBar.setValue(0)

        for scene in self.data_list:
            opencloudrender.download_image_s3( self.ui.dataBucketName.text() , scene[0] , progress_bar=self.ui.uploadProgressBar )

    def dragEnterEvent(self, e):

        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        pathList=e.mimeData().urls()
        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        for url in pathList:
            path=url.toLocalFile()
            if os.path.isfile(path) and path.endswith('.vrscene'):
                vrscene_data = get_vrscene_data_tuple( path )
                self.table_model.add( vrscene_data  )
                self.ui.scenesTableView.resizeColumnsToContents()
            #todo implement folder handling here
        self.emit(QtCore.SIGNAL('layoutChanged()'))

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
        if index.row() == 0:
            return os.path.basename( self.mylist[index.row()][index.column()] )
        else:
            return self.mylist[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        self.mylist = sorted(self.mylist,
            key=operator.itemgetter(col))
        if order == QtCore.Qt.DescendingOrder:
            self.mylist.reverse()
        self.emit(QtCore.SIGNAL('layoutChanged()'))