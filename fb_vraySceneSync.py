import fb_s3IO
def uploadWithDependencies( bucket_name , vrscene_list ):
    for vrscene_path in vrscene_list:
        # deps = [] # getDependencies()
        fb_s3IO.upload_file( bucket_name , vrscene_path )

def getDependencies( ):
    pass
