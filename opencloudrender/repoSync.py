import os
import sys
from s3IO import upload_files,create_folders

# build="31003" or build="24002"
def push( bucket_name , repo_root_dir='/opt/vray' , releaseType="official" , build="" , operating_system="Linux" , host_app="" ):
    """

    :rtype : int
    """
    debug_count=0
    repo_root_dir = '/opt/vray'
    for (source_dir, dir_names, file_names) in os.walk( repo_root_dir ):
        create_folders( bucket_name , source_dir , dir_names  , repo_root_dir )
        if file_names!=[] and source_dir.find( releaseType )>-1 and source_dir.find( build )>-1 and source_dir.find( host_app )>-1 and source_dir.find( operating_system )>-1 or source_dir==repo_root_dir: #source_dir==repo_root_dir is to always update root dir including the vrclient.xml
            # if debug_count < 2: # uncomment this to debug with less files
                print( '{0} ::: {1} ::: {2}'.format( source_dir, dir_names, file_names ) )
                upload_files  ( bucket_name , source_dir , file_names , repo_root_dir , exclude_list = ['/docs/' , '/samples/'] )
                debug_count+=1
    return 0

def pull():
    pass