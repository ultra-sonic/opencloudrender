from PySide import QtCore
import os
import time
import opencloudrender as ocr
from opencloudrender.sceneSync import SyncAssetsThread
from opencloudrender.vrayUtils import get_vrscene_data
from opencloudrender.renderJobSubmission import sendToAfanasy

repo_bucket_name   = os.environ.get( 'VRAY_REPO_BUCKET' , 'env var VRAY_REPO_BUCKET not set!' )
data_bucket_name   = os.environ.get( 'DATA_BUCKET'      , 'env var DATA_BUCKET not set!' )
data_local         = os.environ.get( 'DATA_LOCAL'       , 'env var DATA_LOCAL not set!' )
vrscene_path       = os.path.abspath( './testData/forestInstancer_v039_fbcloudrender_left_stereoCameraLeft.vrscene' )

class TestDummyObject( QtCore.QObject ):
    def __init__(self, parent=None ):
        super(TestDummyObject,self).__init__(parent)
        self.exiting = False
        self.data_list = []
        self.data_bucket_name = None
    def uploadWithDependencies(self , data_bucket_name , vrscene_path ):
        self.data_list.append( get_vrscene_data( vrscene_path ) )
        self.data_bucket_name =  data_bucket_name
        syncAssetsThread = SyncAssetsThread( parent=self ) # call with self as parent
        syncAssetsThread.update_progress_signal.connect( self.setProgress )
        syncAssetsThread.finished.connect( self.finished )
        syncAssetsThread.start()
        while self.exiting==False:
            time.sleep( 1 )
            print "looping"

    def setProgress(self, progress_message , progress_current , progress_max ):
        print( str( progress_current ) + ' / ' + str(progress_max) + ' : ' + progress_message )
    def finished(self):
        print "Finished!"
        self.exiting = True


def test_s3_fileio():
    #vrayRepoSync.push( repo_bucket_name )
    print "test_s3_fileio()"
    TestDummyObject().uploadWithDependencies( data_bucket_name , vrscene_path )

def test_afanasySubmit():
    print "test_afanasySubmit"
    sendToAfanasy(  vrscene_path, priority=50 )

def test_s3_folderIO():
    print "test_s3_folderIO"
    folder_name = '/official/00002/test/jjj/uiguig/hhh'
    folder_name = ocr.s3IO.create_folder( repo_bucket_name , folder_name , recursive=True )
    ocr.s3IO.test_permissions( repo_bucket_name , folder_name )

def test_getOutputImagePath():
    print "test_getOutputImagePath"
    img_path_tuple = ocr.renderJobSubmission.get_output_image_path( vrscene_path )
    print img_path_tuple

def test_getVraySettings():
    print "test_getVraySettings"
    vray_settings = ocr.renderJobSubmission.get_vray_settings( vrscene_path )
    print vray_settings


def test_upload_image_s3():
    print "test_upload_image_s3"
    exr = '/data_local/blackout/volume1/DEFAULT_PROJECT/04_CGI/_workarea/omarkowski/MAYA/images/masterLayer/cloudtest_v002/persp1/cloudtest_v002_masterLayer.exr'
    ocr.upload_image_s3( vrscene_path  , exr , data_local , 3 , 3 , 1 )

def test_getDependencies():
    print "test_getDependencies"
    assets = ocr.sceneSync.getVrsceneDependencies( vrscene_path )
    print assets

test_upload_image_s3()
test_getDependencies()
#test_s3_fileio() # todo debug why signals are not comming through ... ah ... maybe because i don't have a QApplication or something...
test_s3_folderIO()
test_getVraySettings()
test_afanasySubmit()
