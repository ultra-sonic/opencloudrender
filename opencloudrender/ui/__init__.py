from PySide import QtGui,QtCore
import os
import ocrSubmit
import operator
from opencloudrender.renderJobSubmission import SubmitScenesThread
from opencloudrender.sceneSync import SyncAssetsThread, SyncImagesThread
from opencloudrender.vrayUtils    import get_vrscene_data

#todo redirect stdout to a log textfield

class ControlMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)

        self.header = [ 'scenepath', 'start', 'end', 'camera' , 'submit' , 'synced' ]
        self.data_list = []
        self.table_model = ScenesTableModel(self, self.header) #maybe skip passing of data_list and header and use parent.data_list in ScenesTableModel
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

        #Dropdowns
        self.ui.mantraVersionComboBox.addItem('14.0.258')

        self.ui.arnoldVersionComboBox.addItem('4.2.4.1')

        self.ui.vrayVersionComboBox.addItem('30001')
        self.ui.vrayVersionComboBox.addItem('24002')

        #Labels
        self.ui.progressMessagelabel.setText( '' )

    def syncAssets(self):
        self.data_list = self.table_model.getData()
        syncAssetsThread = SyncAssetsThread( parent=self ) # call with self as parent
        syncAssetsThread.update_progress_signal.connect( self.setProgress )
        syncAssetsThread.increment_progress_signal.connect( self.incrementProgress )
        syncAssetsThread.update_status_signal.connect( self.setStatus )
        syncAssetsThread.scene_synced_signal.connect( self.setSceneSynced )
        syncAssetsThread.started.connect( self.disableAllButtons )
        syncAssetsThread.terminated.connect( self.ui.syncAssetsButton.setEnabled )
        syncAssetsThread.finished.connect( self.enableAllButtons )
        self.ui.cancelButton.clicked.connect( syncAssetsThread.cancel )
        syncAssetsThread.start()

    def setSceneSynced(self , scene_path ):
        self.table_model.setSynced( scene_path )

    def submitScenes(self):
        self.data_list = self.table_model.getData()
        submitScenesThread = SubmitScenesThread( parent=self ) # call with self as parent
        submitScenesThread.update_progress_signal.connect( self.setProgress )
        submitScenesThread.started.connect( self.disableAllButtons )
        submitScenesThread.terminated.connect( self.enableAllButtons )
        submitScenesThread.finished.connect( self.enableAllButtons )
        self.ui.cancelButton.clicked.connect( submitScenesThread.cancel )
        submitScenesThread.start()

    def syncImages(self):
        self.data_list = self.table_model.getData()
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
                vrscene_data = get_vrscene_data( path )
                self.table_model.add( vrscene_data  )
                self.ui.scenesTableView.resizeColumnsToContents()
            #todo implement folder handling here
        self.emit(QtCore.SIGNAL('layoutChanged()'))

    def setStatus(self, status_message ):
        self.ui.progressMessagelabel.setText( status_message )

    def setProgress(self, progress_message , progress_current , progress_max ):
        self.ui.progressBar.setMaximum( progress_max )
        self.ui.progressBar.setValue( progress_current )
        self.setStatus( progress_message )
        print( str( progress_current ) + ' / ' + str(progress_max) + ' : ' + progress_message )

    def incrementProgress(self , increment ):
        progress_current = self.ui.progressBar.value()
        self.ui.progressBar.setValue( progress_current + increment )

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
    def __init__(self, parent, header, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.scene_data_list = []
        self.header = header
    def add( self , vrscene_data ):
        if vrscene_data not in self.scene_data_list:
            self.scene_data_list.append( vrscene_data )
            self.sort( 0 , QtCore.Qt.AscendingOrder )

    def rowCount(self, parent):
        return len(self.scene_data_list)

    def columnCount(self, parent):
        if len(self.scene_data_list):
            return len(self.scene_data_list[0])
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
    def setSynced(self , scene_path ):
        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        for scene in self.scene_data_list:
            if scene[0] == scene_path:
                scene[5] = True
                break
        self.emit(QtCore.SIGNAL('layoutChanged()'))

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter
        if index.column() == 0:
            return os.path.basename( self.scene_data_list[index.row()][index.column()] )
        else:
            return self.scene_data_list[index.row()][index.column()]

    def getData(self):
        return self.scene_data_list

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        self.scene_data_list = sorted(self.scene_data_list,
            key=operator.itemgetter(col))
        if order == QtCore.Qt.DescendingOrder:
            self.scene_data_list.reverse()
        self.emit(QtCore.SIGNAL('layoutChanged()'))