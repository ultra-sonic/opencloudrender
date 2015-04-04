import os , sys , afanasySubmit , s3IO , sceneSync
from opencloudrender.vray_utils import get_vray_settings
from path_utils import validate_file_path, add_padding_to_image_path

from PySide.QtCore import *
from PySide import QtGui
#from ui import modelViewTest
import ui

data_bucket_name        = os.environ.get('DATA_BUCKET' , 'env var DATA_BUCKET not set!' )
print "S3 Data Bucket: " + data_bucket_name

def showUI():
    app = QtGui.QApplication(sys.argv)
    #win = modelViewTest.MyWindow( )
    #win.show()
    mySW = ui.ControlMainWindow()
    mySW.show()
    sys.exit(app.exec_())

def upload_image_s3( vrscene_path , file_path , strip_path_prefix , start_frame , end_frame , step_size ):
    """
    :rtype : None
    :param vrscene_path:
    :param file_path: 
    :param strip_path_prefix: 
    :param start_frame: 
    :param end_frame: 
    :param step_size: 
    """
    vray_settings = get_vray_settings( vrscene_path )
    padding = vray_settings[ "anim_frame_padding" ]
    for frame_number in range( start_frame , end_frame+1 , step_size ):
        file_path_frame  = add_padding_to_image_path( file_path , padding ) % frame_number
        #data_bucket_name = os.environ['DATA_BUCKET']
        s3IO.upload_file( data_bucket_name , validate_file_path( file_path_frame ) , strip_path_prefix=strip_path_prefix )

def upload_image_ftp( file_path , strip_path_prefix ):
    """
    :rtype : None
    :param file_path: 
    :param strip_path_prefix: 
    """
    pass


def submit_vrscene( vrscene_path ):
    """
    :rtype : None
    :param vrscene_path: 
    """
    #vraySceneSync.uploadWithDependencies( data_bucket_name , vrscene_path )
    afanasySubmit.sendJob(  vrscene_path, priority=50 )

if __name__ == '__main__':
    showUI()