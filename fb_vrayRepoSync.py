import os
import sys
from fb_s3IO import upload_files,create_folders

# build="31003" or build="24002"
def push( bucket_name , releaseType="official" , build="" , operating_system="Linux" , host_app="" ):
    """

    :rtype : int
    """
    debug_count=0
    strip_source_prefix = '/opt/vray'
    for (source_dir, dir_names, file_names) in os.walk( strip_source_prefix ):
        create_folders( bucket_name , source_dir , dir_names  , strip_source_prefix )
        if file_names!=[] and source_dir.find( releaseType )>-1 and source_dir.find( build )>-1 and source_dir.find( host_app )>-1 and source_dir.find( operating_system )>-1 or source_dir==strip_source_prefix: #source_dir==strip_source_prefix is to always update root dir including the vrclient.xml
            # if debug_count < 2: # uncomment this to debug with less files
                print( '{0} ::: {1} ::: {2}'.format( source_dir, dir_names, file_names ) )
                upload_files  ( bucket_name , source_dir , file_names , strip_source_prefix )
                debug_count+=1
    return 0

def pull():
    pass