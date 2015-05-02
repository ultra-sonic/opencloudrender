from PySide import QtCore
import glob
import logging
import os
import s3IO

# build="31003" or build="24002"
def push( bucket_name , repo_root_dir='/opt/vray' , releaseType="official" , build="" , operating_system="Linux" , host_app="" ):
    """

    :rtype : int
    """
    debug_count=0
    repo_root_dir = '/opt/vray'
    for (source_dir, dir_names, file_names) in os.walk( repo_root_dir ):
        s3IO.create_folders( bucket_name , source_dir , dir_names  , repo_root_dir )
        if file_names!=[] and source_dir.find( releaseType )>-1 and source_dir.find( build )>-1 and source_dir.find( host_app )>-1 and source_dir.find( operating_system )>-1 or source_dir==repo_root_dir: #source_dir==repo_path_glob is to always update root dir including the vrclient.xml
            # if debug_count < 2: # uncomment this to debug with less files
                logging.debug( '{0} ::: {1} ::: {2}'.format( source_dir, dir_names, file_names ) )
                s3IO.upload_files  ( bucket_name , source_dir , file_names , repo_root_dir , exclude_list = ['/docs/' , '/samples/'] )
                debug_count+=1
    return 0

def pull():
    pass

class SyncRepositoryThread(QtCore.QThread):
    update_progress_signal = QtCore.Signal( str , int , int ) #create a custom signal we can subscribe to to emit update commands
    increment_progress_signal = QtCore.Signal( float ) #create a custom signal we can subscribe to to emit update commands
    update_status_signal = QtCore.Signal( str ) #create a custom signal we can subscribe to to emit update commands
    # repo_synced_signal = QtCore.Signal( str )

    def __init__(self , repo_bucket_name , repo_path_glob , strip_path_prefix , build_revision , exclude_list_comma_separated ):
        super(SyncRepositoryThread,self).__init__()
        self.repo_path_glob    = repo_path_glob
        self.strip_path_prefix = strip_path_prefix
        self.repo_bucket_name  = repo_bucket_name
        self.build_revision    = build_revision
        self.exclude_list      = exclude_list_comma_separated.split(',')
        self.exiting           = False

    def run(self):
        self.update_status_signal.emit( 'Start syncing {0} to S3...'.format(self.repo_path_glob) )

        debug_count=0
        operating_system = 'Linux'

        resolved_glob = glob.glob( self.repo_path_glob )
        print resolved_glob
        glob_dirs=[]
        for path in resolved_glob:
            if os.path.isdir( path ):
                glob_dirs.append( path )
            elif os.path.isfile( path ):
                dir_path = os.path.dirname(path)
                if dir_path not in glob_dirs:
                    glob_dirs.append( dir_path )

        print glob_dirs
        for path in glob_dirs:
                for (source_dir, dir_names, file_names) in os.walk( path ):
                    s3IO.create_folders( self.repo_bucket_name , source_dir , dir_names , strip_source_prefix = self.strip_path_prefix )
                    if file_names!=[] and source_dir.find( self.build_revision )>-1 and source_dir.find( operating_system )>-1 or source_dir==self.strip_path_prefix: #source_dir==repo_path_glob is to always update root dir including the vrclient.xml
                        # if debug_count < 2: # uncomment this to debug with less files
                            logging.debug( '{0} ::: {1} ::: {2}'.format( source_dir, dir_names, file_names ) )
                            s3IO.upload_files  ( bucket_name=self.repo_bucket_name , source_dir=source_dir , upload_file_names_list=file_names , strip_path_prefix=self.strip_path_prefix , exclude_list = self.exclude_list )
                            debug_count+=1
        # return 0

    @QtCore.Slot()
    def cancel(self):
        self.exiting = True