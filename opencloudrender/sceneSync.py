import os
from PySide import QtCore
from opencloudrender.pathUtils import validate_file_path, add_padding_to_image_path
from opencloudrender.vrayUtils import getVrsceneDependencies, get_vray_settings
import s3IO

class SyncAssetsThread(QtCore.QThread):
    # thx to those guys I made threading work ;)
    # http://stackoverflow.com/questions/20657753/python-pyside-and-progress-bar-threading
    # http://www.matteomattei.com/pyside-signals-and-slots-with-qthread-example/

    update_progress_signal = QtCore.Signal( str , int , int ) #create a custom signal we can subscribe to to emit update commands
    scene_synced_signal = QtCore.Signal( str )

    def __init__(self, parent=None ):
        super(SyncAssetsThread,self).__init__(parent)
        self.exiting = False
        self.data_list = parent.data_list
        print self.data_list
        self.data_bucket_name = parent.data_bucket_name

    def run( self ):
        self.update_progress_signal.emit( 'Start syncing assets to S3...' , 0 , 100 )

        for scene in self.data_list:
            #convert uploadWithDependencies to an object for cancel funcion
            scene_path = scene[0]
            scene_basename=os.path.basename( scene_path )
            print "DEBUG scene_path: " + scene_path
            ret = 0
            progress_current = 0

            if scene_path.endswith('.vrscene'):
                dependencies = getVrsceneDependencies( scene_path )
            elif scene_path.endswith('.ass'):
                dependencies = getAssDependencies( scene_path )
            elif scene_path.endswith('.ifd'):
                dependencies = getIFDDependencies( scene_path )

            progress_100 = len( dependencies )+1

            for asset in dependencies:
                if self.exiting==False:
                    if s3IO.upload_file( self.data_bucket_name , asset ) != 0:
                        ret=1
                    progress_current=progress_current+1
                    self.update_progress_signal.emit( scene_basename + ' : ' + os.path.basename( asset ) , progress_current , progress_100 )
                else:
                    self.update_progress_signal.emit( scene_basename + ' : sync canceled by user' , progress_current , progress_100 )
                    return 2 #user abort

            progress_current=progress_current+1
            self.update_progress_signal.emit( scene_path , progress_current , progress_100 )

            if s3IO.upload_file( self.data_bucket_name , scene_path ) != 0:
                ret=1

            if ret != 0:
                self.update_progress_signal.emit( "Warning: Done syncing assets, but some assets could not be uploaded!'" , progress_100 , progress_100 )
                # todo popup dialog
            else:
                self.update_progress_signal.emit( "Done syncing assets to S3..." , progress_100 , progress_100 )
                self.scene_synced_signal.emit( scene_path )

    @QtCore.Slot()
    def cancel(self):
        self.exiting = True

class SyncImagesThread(QtCore.QThread):
    # thx to those guys i mad threading work ;)
    # http://stackoverflow.com/questions/20657753/python-pyside-and-progress-bar-threading
    # http://www.matteomattei.com/pyside-signals-and-slots-with-qthread-example/

    update_progress_signal = QtCore.Signal( str , int , int ) #create a custom signal we can subscribe to to emit update commands

    def __init__(self, parent=None ):
        super(SyncImagesThread,self).__init__(parent)
        self.exiting = False
        self.data_list = parent.data_list
        self.data_bucket_name = parent.data_bucket_name

    def run( self ):
        self.update_progress_signal.emit( 'Start syncing images from S3...' , 0 , 1 )
        for scene in self.data_list:
            #opencloudrender.download_image_s3( self.ui.dataBucketName.text() , scene[0] , progress_bar=self.ui.progressBar )
            # get outout images from vrscene
            # download them from s3
            scene_path = scene[0]
            vray_settings = get_vray_settings( scene_path )
            output_image_path='/'.join( [ validate_file_path( vray_settings[ "img_dir" ] ) , vray_settings[ "img_file" ]  ] )
            padding = vray_settings[ "anim_frame_padding" ]
            start_frame = int(vray_settings['anim_start'])
            end_frame   = int(vray_settings['anim_end'])

            frame_list = []
            for frame_number in range( start_frame , end_frame+1 , 1 ):
                # todo add a listen mode to keep downloading new files as they appear and exit when all files are finished
                file_path_frame  = add_padding_to_image_path( output_image_path , padding ) % frame_number
                frame_list.append( validate_file_path( file_path_frame ) )
            s3IO.download_files( self.data_bucket_name , frame_list , update_progress_signal=self.update_progress_signal )

        self.update_progress_signal.emit( "Done syncing images from S3..." , 1 , 1 )

    @QtCore.Slot()
    def cancel(self):
        self.exiting = True


"""
def download_image_s3( data_bucket_name , scene_path , progress_bar=None , listen=False ):
"""




def getAssDependencies( ass_path ): # todo implement ARNOLD .ass parsing
    return None

def getIFDDependencies( ass_path ): # todo implement HOUDINI .ifd parsing
    return None