# Import afanasy python module ( must be in PYTHONPATH).
import os
import af

def sendJob( vrscene_list, start_frame, end_frame, step_size, priority, preview_frames=False , vray_release_type="official" , vray_build="24002" , host_application="Maya" , host_application_version="2015" ):
    # UI Options -- TODO implement!!
    # renderPreviewFirst=1
    # stepSize = 1
    # priority=50
    # GIonly=0
    # tmpPacketSize=1
    # seqDivMin=1
    # clientGroup='ALL'

    # DONE multi vray versions

    """
    if localFarm==0:
        # get image output directory
        for imagePath in getOutputImageNameList():
            vrayImageDir = os.path.dirname(imagePath)
            # check if the filename matches our convention
            checkPath( vrayImageDir )

            # DRY!!!!! DONT REPEAT YOURSELF!!!
            # create image dir on FTP
            # ####vrayImageDir = vrayImageDir.replace(':','_COLON_') #need to replace : (colon) with the word "_colon_"
            # TODO - den forward-slash hack fixen
            createDirectoryOnFTP( translatePathToFTP( vrayImageDir ) , 'rw')

            # prefix directory with farm paths
            # vrayImageDir = translatePathToFarm( vrayImageDir )
    """

    # Create a job.
    job = af.Job( vrscene_list[0].split( '/' )[-1].rstrip( '.vrscene' ) )

    job.setNeedOS('linux')
    job.setPriority(99)
    #user_name = 'render'
    #job.setUserName( user_name )

    for vrscene_file in vrscene_list:
        output_image_path = getOutputImagePath( vrscene_file )
        AFcmd= u'vray {0} {1} {2} {3} {4} @#@ @#@ {5} {6}'.format( vray_release_type , vray_build , host_application , host_application_version , vrscene_file , step_size , os.path.join( output_image_path[0] , output_image_path[1] ) )

        print AFcmd

        block = af.Block( vrscene_file , 'vray' )
        job.blocks.append(block)

        #block.setWorkingDirectory('/home/' + user_name )

        block.setCommand( str( AFcmd ) , prefix=False )
        # Set block tasks preview command arguments.
        # block.setFiles('jpg/img.%04d.jpg')

        # Set block to numeric type, providing first, last frame and frames per host
        block.setNumeric( int(  start_frame ) , int(  end_frame ), 1 , int( step_size ) )
        block.setNonSequential( True )
        # block.tasks = range(13,17)
        #TODO ein block vorher mit den previewframes

    # Send job to Afanasy server.
    result=job.send()
    return result

def getOutputImagePath( vrscene_path ):
    img_file = None
    img_dir  = None
    with open( vrscene_path , 'r' ) as vrscene:
        for line in vrscene:
            if line.find('img_dir') > -1:
                img_dir = line.split('"')[1]
            if line.find('img_file') > -1:
                img_file = line.split('"')[1]
            if img_file!=None and img_dir!=None:
                return ( img_dir , img_file )
    return None
    #raise OSError("No image output path found!")