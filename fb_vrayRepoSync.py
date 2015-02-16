import os
from fb_s3IO import upload_files,get_files_in_directory

bucket_name = 'vray-repo'

# build="31003" or build="24002"
def push( releaseType="official" , build="" , host_app="" ):
    """

    :rtype : int
    """
    debugCount=0
    sourcePrefix = '/opt/vray'
    for (sourceDir, dirname, filenames) in os.walk( sourcePrefix ):
        if filenames!=[] and sourceDir.find( releaseType )>-1 and sourceDir.find( build )>-1 and sourceDir.find( host_app )>-1:
            if debugCount < 2:
                print( '{0} ::: {1} ::: {2}'.format( sourceDir, dirname, filenames ) )
                upload_files( bucket_name , sourceDir , filenames , sourcePrefix )
                #debugCount+=1
    return 0

def pull():
    pass

push()