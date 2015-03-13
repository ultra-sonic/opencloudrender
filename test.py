import os , vrayRepoSync , vraySceneSync , afanasySubmit , s3IO , utils
from fbcloudrender import upload_image_s3 , submit_vrscene , showUI

vray_repo_bucket_name   = os.environ.get( 'VRAY_REPO_BUCKET' , 'env var VRAY_REPO_BUCKET not set!' )
data_bucket_name        = os.environ.get( 'DATA_BUCKET'      , 'env var DATA_BUCKET not set!' )
data_local              = os.environ.get( 'DATA_LOCAL'       , 'env var DATA_LOCAL not set!' )
vrscene_path =  './testData/forestInstancer_v039_fbcloudrender_left_stereoCameraLeft.vrscene'


def test_s3_fileio():
    #vrayRepoSync.push( vray_repo_bucket_name )
    vraySceneSync.uploadWithDependencies( data_bucket_name , vrscene_path )

def test_afanasySubmit():
    submit_vrscene( vrscene_path )

def test_s3_folderIO():
    folder_name = '/official/00002/test/jjj/uiguig/hhh'
    folder_name = s3IO.create_folder( vray_repo_bucket_name , folder_name , recursive=True )
    s3IO.test_permissions( vray_repo_bucket_name , folder_name )

def test_getOutputImagePath():
    img_path_tuple = afanasySubmit.get_output_image_path( vrscene_path )
    print img_path_tuple

def test_getVraySettings():
    vray_settings = afanasySubmit.get_vray_settings( vrscene_path )
    print vray_settings


def test_getAnimStartEnd():
    start_end_tuple = afanasySubmit.get_anim_start_end( vrscene_path )
    print start_end_tuple

def test_upload_image_s3():
    exr = '/data_local/blackout/volume1/DEFAULT_PROJECT/04_CGI/_workarea/omarkowski/MAYA/images/masterLayer/cloudtest_v002/persp1/cloudtest_v002_masterLayer.exr'
    upload_image_s3( vrscene_path  , exr , data_local , 3 , 3 , 1 )

def test_getDependencies():
    assets = vraySceneSync.getDependencies( vrscene_path )
    print assets


#test_upload_image_s3()
#test_getDependencies()
#test_s3_fileio()
#test_s3_folderIO()
#test_afanasySubmit()
#test_getVraySettings()
showUI()
#test_getOutputImagePath()
#test_getAnimStartEnd()