from PySide import QtGui,QtCore
import os
import ocrSubmit
import operator
import opencloudrender
from opencloudrender.afanasySubmit import sendJob
from opencloudrender.sceneSync import SyncAssetsThread, SyncImagesThread
from opencloudrender.vray_utils    import get_vrscene_data_tuple

#todo redirect stdout to a log textfield

class ControlMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)

        self.header = [ 'scenepath', 'start', 'end', 'camera' , 'submit' , 'synced' ]
        self.data_list = []
        self.table_model = ScenesTableModel(self, self.data_list, self.header) #maybe skip passing of data_list and header and use parent.data_list in ScenesTableModel
        self.data_bucket_name = "fbcloudrender-testdata"
        #UI

        self.ui =  ocrSubmit.Ui_OpenCloudRenderSubmit()
        self.ui.setupUi(self)

        #Table
        self.ui.scenesTableView.setModel( self.table_model )

        #Threads
        #self.syncAssetsThread = SyncAssetsThread( )
        #self.syncAssets.update_progress_signal.connect(self.setProgress)

        #Buttons
        self.ui.syncAssetsButton.clicked.connect( self.syncAssets )
        self.ui.submitScenesButton.clicked.connect( self.submitScenes ) # todo disable before sync is not pressed - maybe force-enable it through double-click
        self.ui.syncImagesButton.clicked.connect( self.syncImages )

        #Buckets
        self.ui.dataBucketName.setText( os.environ.get( 'DATA_BUCKET'      , 'fbcloudrender-testdata' ) ) #todo implement this as an .openclouderender json file
        self.ui.repoBucketName.setText( os.environ.get( 'VRAY_REPO_BUCKET' , 'vray-repo' ) )

        #Dropdown
        self.ui.vrayVersionComboBox.addItem('30001')
        self.ui.vrayVersionComboBox.addItem('24002')

        #Labels
        self.ui.progressMessagelabel.setText( '' )




    """def syncAssets(self):
        self.ui.progressBar.setValue(0) # todo - add cancel button

        for scene in self.data_list:
            if uploadWithDependencies( self.ui.dataBucketName.text() , scene[0] , progress_bar=self.ui.progressBar ) != 0:
                print 'ERROR: some assets could not be uploaded!'
    """
    def syncAssets(self):
        #syncAssetsThread = SyncAssetsThread( self , self.data_list , self.ui.dataBucketName.text() )
        syncAssetsThread = SyncAssetsThread( parent=self ) # call with self as parent
        syncAssetsThread.update_progress_signal.connect( self.setProgress )
        syncAssetsThread.started.connect( self.disableAllButtons )
        syncAssetsThread.terminated.connect( self.ui.syncAssetsButton.setEnabled )
        syncAssetsThread.finished.connect( self.enableAllButtons )
        self.ui.cancelButton.clicked.connect( syncAssetsThread.cancel )
        syncAssetsThread.start()

    def submitScenes(self):
        self.ui.progressBar.setValue(0)

        for scene in self.data_list:
            if uploadWithDependencies( self.ui.dataBucketName.text() , scene[0] , progress_bar=self.ui.progressBar ) != 0:
                print 'ERROR: some assets could not be uploaded! SUBMITTING ANYWAY FOR NOW - beta phase!'  #todo do not submit at final release! uncomment next line
                #raise "Aborting!"
            sendJob( scene[0] , priority=50 , vray_build=self.ui.vrayVersionComboBox.currentText() )

    def syncImages(self):
        syncImagesThread = SyncImagesThread( parent=self ) # call with self as parent
        syncImagesThread.update_progress_signal.connect( self.setProgress )
        syncImagesThread.started.connect( self.disableAllButtons )
        syncImagesThread.terminated.connect( self.enableAllButtons )
        syncImagesThread.finished.connect( self.enableAllButtons )
        self.ui.cancelButton.clicked.connect( syncImagesThread.cancel )
        syncImagesThread.start()

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

    def setProgress(self, progress_message , progress_current , progress_max ):
        self.ui.progressBar.setMaximum( progress_max )
        self.ui.progressBar.setValue( progress_current )
        self.ui.progressMessagelabel.setText( progress_message )
        print( str( progress_current ) + ' / ' + str(progress_max) + ' : ' + progress_message )

    def enableAllButtons(self):
        self.ui.syncAssetsButton.setEnabled(True)
        self.ui.submitScenesButton.setEnabled(True)
        self.ui.syncImagesButton.setEnabled(True)
        self.ui.cancelButton.setEnabled(False)

    def disableAllButtons(self):
        self.ui.syncAssetsButton.setEnabled(False)
        self.ui.submitScenesButton.setEnabled(False)
        self.ui.syncImagesButton.setEnabled(False)
        self.ui.cancelButton.setEnabled(True)




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


    def flags(self, index ):
        if index.column() == 1 or index.column() == 2:
            flags = QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
            return flags
        else:
            return QtCore.Qt.ItemIsEnabled
    """
    def setData(self, index, value):
        self.arraydata[index.row()][index.column()] = value
        return True
    """

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter
        if index.column() == 0:
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