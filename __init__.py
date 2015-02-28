import os
import vrayRepoSync , vraySceneSync , afanasySubmit , s3IO , utils
from utils import validate_file_path

vray_repo_bucket_name   = 'vray-repo'               # TODO goes into UI
vrscene_bucket_name     = 'fbcloudrender-testdata'  # TODO goes into UI
vrscene_list = [ '/blackout/volume1/DEFAULT_PROJECT/04_CGI/_workarea/omarkowski/MAYA/cloudtest_v002.vrscene' ]

def showUI():
    pass

def test_s3_fileio():
    #vrayRepoSync.push( vray_repo_bucket_name )
    vraySceneSync.uploadWithDependencies( vrscene_bucket_name , vrscene_list )

def test_afanasySubmit():
    start_frame = 1
    end_frame   = 1
    step_size   = 1
    priority    = 99
    afanasySubmit.sendJob(  vrscene_list, priority=50 )

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

def upload_image_s3( vrscene , file_path , strip_path_prefix , start_frame , end_frame , step_size ):
    padding = afanasySubmit.get_anim_frame_padding( vrscene )
    for frame_number in range( start_frame , end_frame+1 , step_size ):
        file_path_frame = afanasySubmit.add_padding_to_image_path( file_path , padding ) % frame_number
        s3IO.upload_file( vrscene_bucket_name , validate_file_path( file_path_frame ) , strip_path_prefix=strip_path_prefix )

def upload_image_ftp( file_path , strip_path_prefix ):
    pass


#upload_image_s3( '/blackout/volume1/DEFAULT_PROJECT/04_CGI/_workarea/omarkowski/MAYA/cloudtest_v002.vrscene' , '/data_local/blackout/volume1/DEFAULT_PROJECT/04_CGI/_workarea/omarkowski/MAYA/images/masterLayer/cloudtest_v002/persp1/cloudtest_v002_masterLayer.exr' , '/data_local' , 3 , 3 , 1 )
#test_s3_fileio()
#test_s3_folderIO()
#test_afanasySubmit()
#test_getOutputImagePath()
#test_getAnimStartEnd()
