import os

def validate_file_path( file_path ):
    valid_path = os.path.normpath( file_path ).replace('\\' , '/')
    if valid_path.find( ':') > -1 or valid_path.startswith('/')==False:
            raise Exception ("Filepath not supported for ")
    return valid_path
