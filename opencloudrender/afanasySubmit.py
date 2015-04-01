# Import afanasy python module ( must be in PYTHONPATH).
import os , af
from path_utils import validate_file_path
from vray_utils import get_vray_settings


def sendJob( vrscene_path , step_size=1 , start_frame_override = -1 , end_frame_override = -1 , priority=99 , preview_frames=False , vray_release_type="official" , vray_build="24002" , host_application="Maya" , host_application_version="2015" ):
    # UI Options -- TODO implement!!

    # Create a job.
    jobname = os.path.basename( vrscene_path ).rstrip( '.vrscene' )
    job = af.Job( jobname )

    job.setNeedOS('linux')
    job.setPriority( priority )

    vray_settings = get_vray_settings( validate_file_path( vrscene_path ) )
    output_image_path =(  validate_file_path( vray_settings[ "img_dir" ] ) , vray_settings[ "img_file" ]  )
    # anim_start_end = get_anim_start_end   (                     vrscene_path   ) # no validation needed anymore
    start_frame = vray_settings['anim_start']
    end_frame   = vray_settings['anim_end']
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
