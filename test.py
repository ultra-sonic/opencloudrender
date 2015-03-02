import os , vrayRepoSync , vraySceneSync , afanasySubmit , s3IO , utils
from fbcloudrender import upload_image_s3

vray_repo_bucket_name   = os.environ['VRAY_REPO_BUCKET']
data_bucket_name        = os.environ['DATA_BUCKET']
data_local              = os.environ['DATA_LOCAL']
vrscene_list = [ '/blackout/volume1/DEFAULT_PROJECT/04_CGI/_workarea/omarkowski/MAYA/cloudtest_v004.vrscene' ]


def test_s3_fileio():
    vrayRepoSync.push( vray_repo_bucket_name )
    vraySceneSync.uploadWithDependencies( data_bucket_name , vrscene_list )

def test_afanasySubmit():
    vraySceneSync.uploadWithDependencies( data_bucket_name , vrscene_list )
    #afanasySubmit.sendJob(  vrscene_list, priority=50 )

def test_s3_folderIO():
    folder_name = '/official/00002/test/jjj/uiguig/hhh'
    folder_name = s3IO.create_folder( vray_repo_bucket_name , folder_name , recursive=True )
    s3IO.test_permissions( vray_repo_bucket_name , folder_name )

def test_getOutputImagePath():
    img_path_tuple = afanasySubmit.get_output_image_path( vrscene_list[0] )
    print img_path_tuple

def test_getAnimStartEnd():
    start_end_tuple = afanasySubmit.get_anim_start_end( vrscene_list[0] )
    print start_end_tuple

def test_upload_image_s3():
    exr = '/data_local/blackout/volume1/DEFAULT_PROJECT/04_CGI/_workarea/omarkowski/MAYA/images/masterLayer/cloudtest_v002/persp1/cloudtest_v002_masterLayer.exr'
    upload_image_s3( vrscene_list[0]  , exr , data_local , 3 , 3 , 1 )

def test_getDependencies():
    assets = vraySceneSync.getDependencies( vrscene_list[0] )
    print assets


#test_upload_image_s3()
#test_getDependencies()
#test_s3_fileio()
#test_s3_folderIO()
test_afanasySubmit()
#test_getOutputImagePath()
#test_getAnimStartEnd()