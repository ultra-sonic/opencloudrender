from fb_s3IO import upload_files,get_files_in_directory

bucket_name = 'vray_repo'

def push( releaseType="*" , build="*" , host_app="*" ):
    sourceDir = "/opt/vray"
    allFiles = get_files_in_directory( sourceDir )
    upload_files( bucket_name , sourceDir , allFiles )

def pull():
    pass