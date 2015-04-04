from PySide import QtCore
from opencloudrender.vray_utils import getVrsceneDependencies
import s3IO

class SyncAssetsThread(QtCore.QThread):
    # thx to those guys i mad threading work ;)
    # http://stackoverflow.com/questions/20657753/python-pyside-and-progress-bar-threading
    # http://www.matteomattei.com/pyside-signals-and-slots-with-qthread-example/

    update_progress_signal = QtCore.Signal( str , int , int ) #create a custom signal we can subscribe to to emit update commands

    def __init__(self, parent=None ):
        super(SyncAssetsThread,self).__init__(parent)
        self.exiting = False
        self.data_list = parent.data_list
        self.data_bucket_name = parent.data_bucket_name

    def run( self ):
        self.update_progress_signal.emit( 'Start syncing assets...' , 0 , 100 )

        for scene in self.data_list:
            #convert uploadWithDependencies to an object for cancel funcion
            scene_path = scene[0]
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
                    self.update_progress_signal.emit( asset , progress_current , progress_100 )
                else:
                    self.update_progress_signal.emit( 'sync canceled by user' , progress_current , progress_100 )
                    return 2 #user abort

            self.update_progress_signal.emit( scene_path , 99 , 100 )

            if s3IO.upload_file( self.data_bucket_name , scene_path ) != 0:
                ret=1

            if ret != 0:
                self.update_progress_signal.emit( "Warning: Done syncing assets, but some assets could not be uploaded!'" , 100 , 100 )
                return 1
            else:
                self.update_progress_signal.emit( "Done syncing assets..." , 100 , 100 )
                return 0

    @QtCore.Slot()
    def cancel(self):
        self.exiting = True


"""
def uploadWithDependencies( bucket_name , vrscene_path , update_progress_signal=QtCore.Signal() ):
    pass
"""



def getAssDependencies( ass_path ): # todo implement ARNOLD .ass parsing
    return None

def getIFDDependencies( ass_path ): # todo implement HOUDINI .ifd parsing
    return None