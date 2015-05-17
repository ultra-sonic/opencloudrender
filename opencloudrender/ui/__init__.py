import logging
from PySide import QtGui,QtCore
import os,json
import ocrSubmit
import operator
from opencloudrender import vrayUtils
from opencloudrender.renderJobSubmission import SubmitScenesThread
from opencloudrender.repoSync import SyncRepositoryThread
from opencloudrender.sceneSync import SyncAssetsThread, SyncImagesThread
from opencloudrender.vrayUtils    import get_vrscene_data

home = os.path.expanduser('~')
config_file_path = os.path.join( home , '.opencloudrender' )

class ControlMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)

        self.header = [ 'scenepath', 'start', 'end', 'camera' , 'submit' , 'synced' ,  'renderer build' ]
        # self.scene_data_list = []
        self.table_model = ScenesTableModel(self, self.header) #maybe skip passing of scene_data_list and header and use parent.scene_data_list in ScenesTableModel
        self.data_bucket_name = "fbcloudrender-testdata"
        # UI

        self.ui =  ocrSubmit.Ui_OpenCloudRenderSubmit()
        self.ui.setupUi(self)

        # User config
        self.user_config={}
        self.loadUserConfig()

        # Table
        self.ui.scenesTableView.setModel( self.table_model )

        # Threads - need to be assigned to a non-local variable so they won't get garbage collected as described here:
        # http://stackoverflow.com/questions/15702782/qthread-destroyed-while-thread-is-still-running
        self.syncAssetsThread   = None
        self.submitScenesThread = None
        self.syncImagesThread   = None
        self.syncRepositoryThread   = None

        # Buttons
        self.ui.addScenesButton.clicked.connect( self.addScenes )
        self.ui.syncAssetsButton.clicked.connect( self.syncAssets )
        self.ui.submitScenesButton.clicked.connect( self.submitScenes )
        self.ui.syncImagesButton.clicked.connect( self.syncImages )
        self.ui.vrayRepoSyncButton.clicked.connect( self.syncVrayRepository )
        self.ui.vrayInstallButton.clicked.connect( self.installVray )

        # Buckets
        self.ui.dataBucketName.setText( self.user_config.get( 'DATA_BUCKET'      , 'fbcloudrender-testdata' ) )
        self.ui.dataBucketName.textChanged.connect( lambda value : self.setConfig( 'DATA_BUCKET' , value ) )

        self.ui.repoBucketName.setText( self.user_config.get( 'VRAY_REPO_BUCKET' , 'vray-repo' ) )
        self.ui.repoBucketName.textChanged.connect( lambda value : self.setConfig( 'VRAY_REPO_BUCKET' , value ) )

        # Dropdowns
        self.ui.mantraVersionComboBox.addItem('14.0.258')

        self.ui.arnoldVersionComboBox.addItem('4.2.4.1')

        # todo - check repo bucket for existing versions instead of hardcoding them here
        self.ui.vrayVersionComboBox.addItem('31003')
        self.ui.vrayVersionComboBox.addItem('24002')

        vrayVersionComboBox_index = self.ui.vrayVersionComboBox.findText( self.user_config.get('VRAY_VERSION' , '31003' ) )
        if vrayVersionComboBox_index > -1:
            self.ui.vrayVersionComboBox.setCurrentIndex( vrayVersionComboBox_index )
        self.ui.vrayVersionComboBox.currentIndexChanged.connect( lambda : self.setConfig( 'VRAY_VERSION' , self.ui.vrayVersionComboBox.currentText() ) )

        # Labels

    def showErrorMessage(self , error_msg ):
        # todo DRY
        logging.error( error_msg )
        box = QtGui.QMessageBox( self )
        box.setText( error_msg )
        box.show()


    def installVray(self):
        file_path, _ = QtGui.QFileDialog.getOpenFileName(self, 'Choose Linux installer zip-files for VRay...' , filter=("zip files (vraystd*linux*x64*.zip)") )
        vray_repo_glob = self.ui.vrayRepoPathGlob.text()
        if os.path.isdir( vray_repo_glob ):
            vray_repo_root = vray_repo_glob
        else:
            vray_repo_root = os.path.dirname( vray_repo_glob )
        install_thread = vrayUtils.InstallFromZipThread( file_path , vray_repo_root , parent=self )
        install_thread.show_error_signal.connect( self.showErrorMessage )
        install_thread.start()

    def setConfig(self , key , value ):
        self.user_config[key] = value
        self.saveUserConfig()

    def loadUserConfig(self):
        if os.path.isfile( config_file_path ):
            config_file = open(
                config_file_path,
                mode='r'
            )
            self.user_config = json.load( config_file )
            logging.info( 'loaded configfile from ' + config_file_path)
    def saveUserConfig(self):
        config_file = open(
            config_file_path,
            mode='w'
        )
        json.dump( self.user_config , config_file )
        logging.info( 'saved configfile to ' + config_file_path)

    def addScenes(self):
        file_path, _ = QtGui.QFileDialog.getOpenFileName(self, 'Choose renderable files...' , filter=("renderable files (*.vrscene *.ass *.ifd *.hip)") )
        self.addFile( file_path )


    def syncVrayRepository(self):
        version = self.ui.vrayRepoVersionComboBox.currentText()
        if version == 'all':
            version = ''
        self.syncRepository( self.ui.vrayRepoPathGlob.text() , self.ui.vrayRepoStripPathPrefix.text() , version , self.ui.vrayRepoExcludes.text() )

    def syncRepository(self , path_glob , strip_path_prefix , build_revision , exclude_directories ):
        self.syncRepositoryThread = SyncRepositoryThread( repo_bucket_name=self.ui.repoBucketName.text() , repo_path_glob=path_glob , strip_path_prefix=strip_path_prefix ,  build_revision=build_revision , exclude_list_comma_separated=exclude_directories )
        self.syncRepositoryThread.update_progress_signal.connect( self.setProgress )
        self.syncRepositoryThread.increment_progress_signal.connect( self.incrementProgress )
        self.syncRepositoryThread.update_status_signal.connect( self.setStatus )
        # self.syncRepositoryThread.repo_synced_signal.connect( self.setSceneSynced )
        # self.syncRepositoryThread.started.connect( self.disableAllButtons )
        # self.syncRepositoryThread.terminated.connect( self.ui.syncAssetsButton.setEnabled )
        # self.syncRepositoryThread.finished.connect( self.enableAllButtons )
        self.ui.cancelButton.clicked.connect( self.syncRepositoryThread.cancel )
        self.syncRepositoryThread.start()

    def syncAssets(self):
        self.syncAssetsThread = SyncAssetsThread( scene_data_list = self.table_model.scene_data_list , data_bucket_name = self.data_bucket_name )
        self.syncAssetsThread.update_progress_signal.connect( self.setProgress )
        self.syncAssetsThread.increment_progress_signal.connect( self.incrementProgress )
        self.syncAssetsThread.update_status_signal.connect( self.setStatus )
        self.syncAssetsThread.scene_synced_signal.connect( self.setSceneSynced )
        self.syncAssetsThread.started.connect( self.disableAllButtons )
        self.syncAssetsThread.terminated.connect( self.ui.syncAssetsButton.setEnabled )

        self.syncAssetsThread.finished.connect( self.enableAllButtons )
        self.syncAssetsThread.finished.connect( self.saveUserConfig )

        self.ui.cancelButton.clicked.connect( self.syncAssetsThread.cancel )
        self.syncAssetsThread.start()

    def setSceneSynced(self , scene_path ):
        logging.debug('scene synced: ' + scene_path)
        self.table_model.setScenepathSynced( scene_path )

    def submitScenes(self):
        self.submitScenesThread = SubmitScenesThread( scene_data_list=self.table_model.scene_data_list )
        self.submitScenesThread.update_progress_signal.connect( self.setProgress )
        self.submitScenesThread.update_status_signal.connect( self.setStatus )
        self.submitScenesThread.started.connect( self.disableAllButtons )
        self.submitScenesThread.terminated.connect( self.enableAllButtons )

        self.submitScenesThread.finished.connect( self.enableAllButtons )
        self.submitScenesThread.finished.connect( self.saveUserConfig )

        self.ui.cancelButton.clicked.connect( self.submitScenesThread.cancel )
        self.submitScenesThread.start()

    def syncImages(self):
        self.syncImagesThread = SyncImagesThread( scene_data_list=self.table_model.scene_data_list , data_bucket_name = self.data_bucket_name )
        self.syncImagesThread.update_progress_signal.connect( self.setProgress )
        self.syncImagesThread.started.connect( self.disableAllButtons )
        self.syncImagesThread.terminated.connect( self.enableAllButtons )
        self.syncImagesThread.finished.connect( self.enableAllButtons )
        self.ui.cancelButton.clicked.connect( self.syncImagesThread.cancel )
        self.syncImagesThread.start()

    def dragEnterEvent(self, e):

        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        logging.debug('accepted dropEvent' )
        pathList=e.mimeData().urls()
        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        for url in pathList:
            path=url.toLocalFile()
            self.addFile( path )
        self.emit(QtCore.SIGNAL('layoutChanged()'))

    def addFile( self , path ):
        if os.path.isfile(path) and path.endswith('.vrscene'):
            vrscene_data = get_vrscene_data( path )
            vray_build = self.ui.vrayVersionComboBox.currentText()
            self.table_model.add( vrscene_data , vray_build ) # extend by default vray version from ui
            self.ui.scenesTableView.resizeColumnsToContents()
        elif os.path.isdir(path):
            logging.debug('Path dropped - unsupported at the moment - sorry!')
        else:
            logging.error( 'Unsupported path:' + path )
        #todo implement folder handling here

    def setStatus(self, status_message ):
        self.ui.statusbar.showMessage( status_message )

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
    def add( self , scene_data , renderer_build ):
        scene_data.append( renderer_build )
        if scene_data not in self.scene_data_list:
            self.scene_data_list.append( scene_data  )
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
        elif index.column() == 4 or index.column() == 5:
            flags = QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
        else:
            flags = QtCore.Qt.ItemIsEnabled
        return flags

    def setData(self, index, value, role):
        #self.arraydata[index.row()][index.column()] = value
        row=index.row()
        col=index.column()
        print "set row/col" + str(row) + "/" + str(col) + " to " + str( value )
        if   col == 1:
            self.setRowStartFrame( row , value )
        elif col == 2:
            self.setRowEndFrame( row , value )
        elif col == 4:
            self.setRowSubmit( row , value )
            return True
        elif col ==5:
            self.setRowSynced( row , value )
            return True
        return False

    def setRowStartFrame(self , row , value):
        # todo - do not alloe setting start/end outside of renderable framebounds
        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        scene = self.scene_data_list[ row ]
        scene[1] = value
        self.emit(QtCore.SIGNAL('layoutChanged()'))

    def setRowEndFrame(self , row , value):
        # todo - do not alloe setting start/end outside of renderable framebounds
        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        scene = self.scene_data_list[ row ]
        scene[2] = value
        self.emit(QtCore.SIGNAL('layoutChanged()'))


    def setScenepathSynced(self , scene_path ):
        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        for scene in self.scene_data_list:
            if scene[0] == scene_path:
                scene[5] = True
                break
        self.emit(QtCore.SIGNAL('layoutChanged()'))

    def setRowSynced(self , row , value):
        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        scene = self.scene_data_list[ row ]
        if value:
            scene[5] = True
        else:
            scene[5] = False
        self.emit(QtCore.SIGNAL('layoutChanged()'))


    def setRowSubmit(self , row , value):
        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        scene = self.scene_data_list[ row ]
        if value:
            scene[4] = True
        else:
            scene[4] = False
        self.emit(QtCore.SIGNAL('layoutChanged()'))

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role == QtCore.Qt.TextAlignmentRole:
            if index.column() != 0:
                return QtCore.Qt.AlignCenter
        elif role == QtCore.Qt.CheckStateRole:
            if index.column() == 4 or index.column() == 5:
                if self.scene_data_list[index.row()][index.column()] == True:
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked
        elif role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return os.path.basename( self.scene_data_list[index.row()][index.column()] )
            else:
                return self.scene_data_list[index.row()][index.column()]
        else:
            return None

    """
    obsolete for now
    def getData(self):
        return self.scene_data_list
    """
    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.header[col]
        return None

    # todo implement right-click menu with a REMOVE command

    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        self.scene_data_list = sorted(self.scene_data_list,
            key=operator.itemgetter(col))
        if order == QtCore.Qt.DescendingOrder:
            self.scene_data_list.reverse()
        self.emit(QtCore.SIGNAL('layoutChanged()'))