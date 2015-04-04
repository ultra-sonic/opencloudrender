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
        self.ui.syncAssetsAndSubmitButton.clicked.connect( self.syncAssetsAndSubmit ) # todo disable before sync is not pressed - maybe force-enable it through double-click
        self.ui.syncImagesButton.clicked.connect( self.syncImages )

        #Buckets
        self.ui.dataBucketName.setText( os.environ.get( 'DATA_BUCKET'      , 'fbcloudrender-testdata' ) ) #todo implement this as an .openclouderender json file
        self.ui.repoBucketName.setText( os.environ.get( 'VRAY_REPO_BUCKET' , 'vray-repo' ) )

        #Dropdown
        self.ui.vrayVersionComboBox.addItem('30001')
        self.ui.vrayVersionComboBox.addItem('24002')




    """def syncAssets(self):
        self.ui.progressBar.setValue(0) # todo - add cancel button

        for scene in self.data_list:
            if uploadWithDependencies( self.ui.dataBucketName.text() , scene[0] , progress_bar=self.ui.progressBar ) != 0:
                print 'ERROR: some assets could not be uploaded!'
    """
    def syncAssets(self):
        self.ui.syncAssetsButton.setEnabled(False)
        self.ui.syncAssetsAndSubmitButton.setEnabled(False)
        self.ui.syncImagesButton.setEnabled(False)
        syncAssetsThread = SyncAssetsThread( self , self.data_list , self.ui.dataBucketName.text() )
        syncAssetsThread.update_progress_signal.connect( self.setProgress )
        syncAssetsThread.progress_done_signal.connect( self.enableButtons )
        syncAssetsThread.start()

    def syncAssetsAndSubmit(self):
        self.ui.progressBar.setValue(0)

        for scene in self.data_list:
            if uploadWithDependencies( self.ui.dataBucketName.text() , scene[0] , progress_bar=self.ui.progressBar ) != 0:
                print 'ERROR: some assets could not be uploaded! SUBMITTING ANYWAY FOR NOW - beta phase!'  #todo do not submit at final release! uncomment next line
                #raise "Aborting!"
            sendJob( scene[0] , priority=50 , vray_build=self.ui.vrayVersionComboBox.currentText() )

    def syncImages(self):
        self.ui.progressBar.setValue(0)
        print "Start syncing images..."
        for scene in self.data_list:
            opencloudrender.download_image_s3( self.ui.dataBucketName.text() , scene[0] , progress_bar=self.ui.progressBar )
        print "Done syncing images..."

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

    def enableButtons(self):
        self.ui.syncAssetsButton.setEnabled(True)
        self.ui.syncAssetsAndSubmitButton.setEnabled(True)
        self.ui.syncImagesButton.setEnabled(True)

    def disaableButtons(self):
        self.ui.syncAssetsButton.setEnabled(False)
        self.ui.syncAssetsAndSubmitButton.setEnabled(False)
        self.ui.syncImagesButton.setEnabled(False)


class SyncAssetsThread(QtCore.QThread):
    # http://stackoverflow.com/questions/20657753/python-pyside-and-progress-bar-threading <<< THIS IS IT!
    # http://stackoverflow.com/questions/12138954/pyside-and-qprogressbar-update-in-a-different-thread


    update_progress_signal = QtCore.Signal( str , int , int ) #create a custom signal we can subscribe to to emit update commands
    progress_done_signal = QtCore.Signal()

    def __init__(self, parent=None, data_list=None , data_bucket_name=None ):
        super(SyncAssetsThread,self).__init__(parent)
        self.exiting = False
        self.parent = parent
        self.data_list = data_list
        self.data_bucket_name = data_bucket_name

    def run( self ):
        self.update_progress_signal.emit( 'checking...' , 0 , 100 )

        for scene in self.parent.data_list:
            if uploadWithDependencies( self.data_bucket_name , scene[0] , update_progress_signal=self.update_progress_signal ) != 0:
                print 'ERROR: some assets could not be uploaded!'
        self.progress_done_signal.emit()

    """@QtCore.Slot(str)
    def cancel(self, text):
        self.solution = text
        # this definitely gets executed upon pressing return
        self.wait_for_input.exit()
    """
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