# Import afanasy python module ( must be in PYTHONPATH).
import af

def sendAFcommand( vrsceneList, startFrame, endFrame, stepSize, priority, previewFrames , vrayVersion=("official" , "24002" , "Maya" , 2015 ) ):
    # UI Options -- TODO implement!!
    # renderPreviewFirst=1
    # stepSize = 1
    # priority=50
    # GIonly=0
    # tmpPacketSize=1
    # seqDivMin=1
    # clientGroup='ALL'

    # DONE multi vray versions

    global localFarm

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


    # Create a job.
    job = af.Job( vrsceneList[0].split( '/' )[-1].rstrip( '.vrscene' ) )

    job.setNeedOS('linux')
    job.setPriority(99)

    job.setUserName( 'render' )

    for vrsceneFile in vrsceneList:
        if localFarm==0:
            AFcmd= u'vray_af ' + str( vrayVersion ) + ' ' + translatePathToFarm( vrsceneFile ).replace( '.vrscene' , '_FBI.vrscene' )
        else:
            AFcmd= u'vray_af ' + str( vrayVersion ) + ' ' + vrsceneFile
        #TODO - FIX FOR FLOAT VALUES FOR FRAMES
        AFcmd += ' @#@' #AF WILL SET STARTFRAME HERE
        AFcmd += ' @#@' #AF WILL SET ENDFRAME HERE
        AFcmd += ' ' + str( int( stepSize ) )
        # print AFcmd

        block = af.Block( vrsceneFile , 'vray' )
        job.blocks.append(block)

        if localFarm==0:
            block.setWorkingDirectory('/home/' + username)

        block.setCommand( str( AFcmd ) )
        # Set block tasks preview command arguments.
        # block.setFiles('jpg/img.%04d.jpg')

        # Set block to numeric type, providing first, last frame and frames per host
        block.setNumeric( int(  startFrame ) , int(  endFrame ), 1 , int( stepSize ) )
        # block.tasks = range(13,17)
        #TODO ein block vorher mit den previewframes

    # Send job to Afanasy server.
    result=job.send()
    return result