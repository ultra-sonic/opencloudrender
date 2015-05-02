import os

def validate_file_path( file_path ):
    valid_path = os.path.normpath( file_path ).replace('\\' , '/')
    if valid_path.find( ':') > -1:
        raise Exception ('Filepath containing ":" not supported for cloudrendering: ' + valid_path )
    if valid_path.startswith('/')==False:
        raise Exception ('Filepath does not start with a "/" and is not supported for cloudrendering - maybe check for quotes around this path: ' + valid_path )
    return valid_path

def strip_file_path( file_path , strip_path_prefix  ):
    #print "In: " + file_path
    if file_path.startswith( strip_path_prefix ):
        stripped_path = file_path[ len( strip_path_prefix ): ]
        #print "Out: " + stripped_path
        return stripped_path
    else:
        return file_path

def add_padding_to_image_path( img_file_path , anim_frame_padding , frame_num_prefix='' ):
    last_dot = img_file_path.rfind('.')
    img_file_with_padding = img_file_path[ : last_dot ] + frame_num_prefix + ".%0{0}d".format( anim_frame_padding ) + img_file_path[ last_dot : ]
    return img_file_with_padding
