# Import afanasy python module ( must be in PYTHONPATH).
import os , af
from utils import validate_file_path

def sendJob( vrscene_path , step_size=1 , start_frame_override = -1 , end_frame_override = -1 , priority=99 , preview_frames=False , vray_release_type="official" , vray_build="24002" , host_application="Maya" , host_application_version="2015" ):
    # UI Options -- TODO implement!!

    # Create a job.
    job = af.Job( vrscene_path.split( '/' )[-1].rstrip( '.vrscene' ) )

    job.setNeedOS('linux')
    job.setPriority( priority )
    #user_name = 'render'
    #job.setUserName( user_name )


    # todo implement full parsing of all vraySettingsOutput parameters into a dict!
    output_image_path  = get_output_image_path( validate_file_path( vrscene_path ) )
    anim_start_end = get_anim_start_end   (                     vrscene_path   ) # no validation needed anymore
    start_frame = anim_start_end[0]
    end_frame   = anim_start_end[1]
    if start_frame_override > -1:
        start_frame = start_frame_override
    if end_frame_override > -1:
        end_frame = end_frame_override

    AFcmd= u'vray {0} {1} {2} {3} {4} @#@ @#@ {5} {6}'.format( vray_release_type , vray_build , host_application , host_application_version , vrscene_path , step_size , os.path.join( output_image_path[0] , output_image_path[1] ) )

    print AFcmd

    block = af.Block( vrscene_path , 'vray' )
    job.blocks.append(block)

    #block.setWorkingDirectory('/home/' + user_name )

    block.setCommand( str( AFcmd ) , prefix=False )
    # Set block tasks preview command arguments.
    # block.setFiles('jpg/img.%04d.jpg')

    # Set block to numeric type, providing first, last frame and frames per host
    block.setNumeric( int(  start_frame ) , int(  end_frame ), 1 , int( step_size ) )
    block.setSequential( 10 )

    # Send job to Afanasy server.
    result=job.send()
    return result



def get_output_image_path( vrscene_path ):
    img_file = None
    img_dir  = None
    with open( vrscene_path , 'r' ) as vrscene:
        for line in vrscene:
            if line.find('img_dir=') > -1:
                img_dir = line.split('"')[1]
            if line.find('img_file=') > -1:
                img_file = line.split('"')[1]
            if img_file!=None and img_dir!=None:
                return ( validate_file_path( img_dir ) , img_file )

    raise Exception("No image_output_path found in vrscene" + vrscene_path )

def add_padding_to_image_path( img_file_path , anim_frame_padding , frame_num_prefix='' ):
    last_dot = img_file_path.rfind('.')
    img_file_with_padding = img_file_path[ : last_dot ] + frame_num_prefix + "%0{0}d".format( anim_frame_padding ) + img_file_path[ last_dot : ]
    return img_file_with_padding

def get_anim_frame_padding( vrscene_path ):
    with open( vrscene_path , 'r' ) as vrscene:
        for line in vrscene:
            if line.find('anim_frame_padding=') > -1:
                anim_frame_padding = line.rstrip(';\n').split('=')[-1]
                return anim_frame_padding
    raise Exception("No anim_frame_padding found in vrscene" + vrscene_path )


def get_anim_start_end( vrscene_path ):
    anim_start = None
    anim_end   = None
    with open( vrscene_path , 'r' ) as vrscene:
        for line in vrscene:
            if line.find('anim_start=') > -1:
                anim_start = line.rstrip(';\n').split('=')[-1]
            if line.find('anim_end=') > -1:
                anim_end  = line.rstrip(';\n').split('=')[-1]
            if anim_start!=None and anim_end!=None:
                return( anim_start , anim_end )
    raise Exception("No anim_start or anim_end found in vrscene" + vrscene_path )