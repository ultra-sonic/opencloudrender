import os
import vrayRepoSync , vraySceneSync , afanasySubmit , s3IO , utils
from utils import validate_file_path

vray_repo_bucket_name   = 'vray-repo'               # TODO goes into UI
vrscene_bucket_name     = 'fbcloudrender-testdata'  # TODO goes into UI
vrscene_list = [ '/blackout/volume1/DEFAULT_PROJECT/04_CGI/_workarea/omarkowski/MAYA/cloudtest_v001.vrscene' ]

def showUI():
    pass

def test_s3_fileio():
    vrayRepoSync.push( vray_repo_bucket_name )
    vraySceneSync.uploadWithDependencies( vrscene_bucket_name , vrscene_list )

def test_afanasySubmit():
    start_frame = 1
    end_frame   = 1
    step_size   = 1
    priority    = 99
    afanasySubmit.sendJob(  vrscene_list, start_frame, end_frame, step_size, priority )

def test_s3_folderIO():
    folder_name = '/official/00002/test/jjj/uiguig/hhh'
    folder_name = s3IO.create_folder( vray_repo_bucket_name , folder_name , recursive=True )
    s3IO.test_permissions( vray_repo_bucket_name , folder_name )

def test_getOutputImagePath():
    img_path_tuple = vraySceneSync.getOutputImagePath( vrscene_list[0] )
    return 0

def upload_image_s3( file_path , strip_path_prefix ):
    s3IO.upload_file( vrscene_bucket_name , validate_file_path( file_path ) , strip_path_prefix=strip_path_prefix )

def upload_image_ftp( file_path , strip_path_prefix ):
    pass


upload_image_s3( '/data_local//blackout/volume1/DEFAULT_PROJECT/04_CGI/_workarea/omarkowski/MAYA//images/_tmpcloudtest_v001.0001.png' , '/data_local' )

#test_s3_fileio()
#test_s3_folderIO()
test_afanasySubmit()
#test_getOutputImagePath()