import os

def validate_file_path( file_path ):
    valid_path = os.path.normpath( file_path ).replace('\\' , '/')
    if valid_path.find( ':') > -1 or valid_path.startswith('/')==False:
            raise Exception ("Filepath not supported for cloudrendering: " + file_path )
    return valid_path

def strip_file_path( file_path , strip_path_prefix  ):
    #print "In: " + file_path
    if file_path.startswith( strip_path_prefix ):
        stripped_path = file_path[ len( strip_path_prefix ): ]
        #print "Out: " + stripped_path
        return stripped_path
    else:
        return file_path