from fb_s3IO import upload_files,get_files_in_directory

bucket_name = 'vray_repo'

def push( releaseType="*" , build="*" , host_app="*" ):
    allFiles = get_files_in_directory( "/opt/vray" )
    upload_files( bucket_name , sourceDir , allFiles )

def pull():
    pass