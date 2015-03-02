import os , afanasySubmit , s3IO
from utils import validate_file_path


#vray_repo_bucket_name   = 'vray-repo'               # TODO goes into UI
#vrscene_bucket_name     = 'fbcloudrender-testdata'  # TODO goes into UI
#vrscene_list = [ '/blackout/volume1/DEFAULT_PROJECT/04_CGI/_workarea/omarkowski/MAYA/cloudtest_v002.vrscene' ]

def showUI():
    pass

def upload_image_s3( vrscene , file_path , strip_path_prefix , start_frame , end_frame , step_size ):
    padding = afanasySubmit.get_anim_frame_padding( vrscene )
    for frame_number in range( start_frame , end_frame+1 , step_size ):
        file_path_frame  = afanasySubmit.add_padding_to_image_path( file_path , padding ) % frame_number
        data_bucket_name = os.environ['DATA_BUCKET']
        s3IO.upload_file( data_bucket_name , validate_file_path( file_path_frame ) , strip_path_prefix=strip_path_prefix )

def upload_image_ftp( file_path , strip_path_prefix ):
    pass