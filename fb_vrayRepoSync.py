import os
import sys
from fb_s3IO import upload_files,get_files_in_directory

# build="31003" or build="24002"
def push( bucket_name , releaseType="official" , build="" , operating_system="Linux" , host_app="" ):
    """

    :rtype : int
    """
    debugCount=0
    sourcePrefix = '/opt/vray'
    for (sourceDir, dirname, filenames) in os.walk( sourcePrefix ):
        if filenames!=[] and sourceDir.find( releaseType )>-1 and sourceDir.find( build )>-1 and sourceDir.find( host_app )>-1 and sourceDir.find( operating_system )>-1 or sourceDir==sourcePrefix: #sourceDir==sourcePrefix is to always update root dir including the vrclient.xml
            if debugCount < 2: # uncomment this to debug with less files
                print( '{0} ::: {1} ::: {2}'.format( sourceDir, dirname, filenames ) )
                upload_files( bucket_name , sourceDir , filenames , sourcePrefix )
                debugCount+=1
    return 0

def pull():
    pass