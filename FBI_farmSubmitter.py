from __future__ import with_statement # this line is only needed for 2008 and 2009
import sys
import os
import maya
import platform
import subprocess

try:
    from pymel.core import *
    from pymel import versions
except:
    raise( error('Pymel not found. Please install from http://code.google.com/p/pymel/downloads/list') )


        
#HIGH PRIO
#_defaultRenderLayer gewichse fixen ... testscene ohne renderlayer

#renderview unterdruecken ... dafuer gibts ein anderes command.!!! hab ich irgendwo schonmal eingebaut...wenn nicht sogar hier in dem py

#DONE - fix wenn kein output image name festgelegt wurde
#TODO
#fix fuer scene OHNE renderlayer
#TODO
#restore function that is called on every error!!! so that all settings are always restored to their previous values!!! even if canceled
#TODO
#SILENCE paramiko im maya script editor

#initialize progressbar

global gMainProgressBar
gMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar');


def initCloudEnv():
    
    #INIT username and key
    keydir=__file__.replace('.pyc','/YOUR_KEYFILE_IN_HERE').replace('.py','/YOUR_KEYFILE_IN_HERE')
    
    #SETUP ENVIRONMENT
    #ADD site-packages to sys.path before importing paramiko - only needed if we didn't install in maya installdir
    sys.path.append( os.path.dirname( __file__ ) + '/Lib/site-packages' )
    import paramiko
    
    #INIT AF_ROOT
    AF_ROOT = __file__.replace('.pyc','/af').replace('.py','/af')
    os.environ['AF_ROOT'] = AF_ROOT
    try:
        system_os = platform.system()
    except:
        system_os = os.uname()[0]
    print 'Operating System: ' + system_os
    sys.path.append( AF_ROOT + '/python' )
    sys.path.append( AF_ROOT + '/' + system_os )
    print 'AF_ROOT = ' + AF_ROOT
    
    
    
    
    #TODO DONE enable logfile
    #paramiko.util.log_to_file(os.path.basename(__file__), level=10)
    
    global ftphome
    ftphome = '/'
    #print keydir
    keys=os.listdir(keydir) 
    global username
    username=""
    for currentKey in keys:
        #DON'T use hidden or zipped files
        if currentKey[0] != '.' and currentKey.find('.zip') == -1:
            username=currentKey
        else:
            pass
    
    if username=="":
        raise( PopupError("No keyfile found. Please extract the zipfile you've received into:\n" + keydir ) )
    
    print 'Username: ' + username
    keyfile=keydir + '/' + username
    
    global key
    key=paramiko.RSAKey.from_private_key_file(keyfile)


class syncFarm():
    def __init__( self ):
        self.fileList=[]
        self.vrsceneList=[]
        self.uploadSize=0
        
    def addFile( self , path ):
        try:
            self.fileList.index( path )
        except:
            self.fileList.append( path )
            #TODO - doch wieder in eigene function auslagern! funzt nicht, wenn eine datei geadded wird, die noch nicht existiert
            #self.uploadSize = self.uploadSize + os.stat( path ).st_size
            
    def addVrscene( self , path ):
        try:
            self.vrsceneList.index( path )
        except:
            self.vrsceneList.append( path )

    def upload( self ):
        uploadFiles( self.fileList )
        #self.clear()
        
    def clear( self ):
        self.__init__()
        
         

def getAllFilesNeeded():
    #TODO progress bar
    #TODO nur filenodes und vraymeshes syncen
    fileList=list()
    
    nodeList = list()
    nodeList.extend( ls(type='file'))
    nodeList.extend( ls(type='VRayMesh') )
    nodeList.extend( ls(type='VRaySimbiont') )
    nodeList.extend( ls(type='VRayMeshMaterial') )
    nodeList.extend( ls(type='psdFileTex') )
    nodeList.extend( ls(type='VRayPtex') )
    nodeList.extend( ls(type='VRayLightIESShape') )
    #TODO - FULL SYNC OPTION
    #nodeList = ls()
    
    for current in nodeList:
            for attr in current.listAttr():
                    if attr.split('.')[-1].lower().find('file')>-1:
                            tmp=getAttr(attr)
                            if type(tmp)==unicode:
                                    #TODO adjust for backslashes later!!!
                                    if tmp.find('/')>-1:
                                            fileList.append(tmp)
                                            #print 'Attr -> '+attr+' Value -> '+tmp

    #print fileList
    #remove duplicates
    fileList = list(set(fileList))
    try:
            fileList.remove(getAttr('vraySettings.vrscene_filename'))
    except:
            pass
            
    try:
            fileList.remove(getAttr('vraySettings.fileNamePrefix'))
    except:
            pass
    
    return fileList

def uploadFiles(fileList):
    global username
    #global transport
    #print type(transport)
    #sftp = paramiko.SFTPClient.from_transport(transport)
    global sftp
    global ftphome
    global gMainProgressBar
    progressBar( gMainProgressBar, edit=True, beginProgress=True, isInterruptable=True, status='uploading files', maxValue=len(fileList) )
    
    for fileName in fileList:
            if progressBar(gMainProgressBar, query=True, isCancelled=True ):
                    break
            
            #check if path matches our conventions!
            checkPath(fileName)
            
            localPath = fileName
            
            fileName=fileName.replace('//','/')   
            
            #sftp.chdir(ftphome + '/' + username)		
            #chroot does this automatically
            
            remotePath = translatePathToFTP( fileName )
            
            #check if file exists and if it needs to be replaced		
            try:
                localStat=paramiko.SFTPAttributes().from_stat(os.stat(localPath))
            except:
                print 'Missing File: ' + localPath
                raise( PopupError( 'There are files missing in this project. Please check script editor' ) )
            
            try:
                    remoteStat=sftp.stat( remotePath )			
                    #print localStat.st_mtime
                    #print remoteStat.st_mtime
                    #print ' Local filesize: ' + str(localStat.st_size)
                    #print 'Remote filesize: ' + str(remoteStat.st_size)
                    #UPLOAD IF LOCAL FILE IS NEWER OR DIFFERENT SIZE
                    if localStat.st_mtime > remoteStat.st_mtime or localStat.st_size <> remoteStat.st_size:
                            try:
                                    sftp.put(localPath, remotePath)
                            except:
                                    #changeSceneSettings('restore')
                                    global sceneSettings
                                    sceneSettings.reset()
                                    confirmDialog(message="Could not upload file:\n" + localPath + '\nSubmission canceled! Please contact:\noliver@fullblownimages.com')
                            #SET ATIME AND MTIME ON SERVER TO LOCAL VALUES
                            sftp.utime( remotePath , tuple( [localStat.st_atime , localStat.st_mtime] ) )
                    else:
                            pass
                            #print localPath + ' is identical on server.'
            except:
                    #MAKE DIR IF IT DOES NOT EXIST
                    try:
                        sftp.stat( dirname( remotePath ) )
                    except:
                            createDirectoryOnFTP( os.path.dirname(remotePath) , 'r')
                            
                    #sftp.put(localPath, ftphome + '/' + username + '/' + remotePath)
                    sftp.put(localPath, remotePath)
                    #SET ATIME AND MTIME ON SERVER TO LOCAL VALUES
                    #sftp.utime(ftphome + '/' + username + '/' + remotePath, tuple( [localStat.st_atime , localStat.st_mtime] ) )
                    sftp.utime( remotePath, tuple( [localStat.st_atime , localStat.st_mtime] ) )
                    
            #DONE PROGRESS BARS UPLOAD!!!
            progressBar(gMainProgressBar, edit=True, step=1)
            
    #sftp.close()
            
    #transport.close()
    progressBar(gMainProgressBar, edit=True, endProgress=True)
    print 'Upload done.'


def createDirectoryOnFTP(dirName , writePermission):
    global username
    global ftphome
    #print 'User: ' + username
    #global transport
    #print type(transport)
    #TODO - statt global transport lieber global sftp object hernehmen
    #sftp = paramiko.SFTPClient.from_transport(transport)
    global sftp
    #print type(sftp)
    
    #sftp.chdir(ftphome + '/' + username)
    #removed - chroot does that

    #dirName=dirName.replace('//','/')
    #cleanup slashes infront an at the end of the directory
    #dirName=dirName.lstrip('/').rstrip('/')
    remotePath = dirName
    #print 'Remotepath: ' + remotePath
    #TODO  - try to listdir and check if it exists before mkdir
    #MAKE DIR IF IT DOES NOT EXIST
    try:
            sftp.stat(  remotePath  )
            #print 'Directory already exists...'
    except:
            #must be made one after another
            recursiveDir=""
            for currentDir in remotePath.split('/'):
                    recursiveDir = recursiveDir +currentDir+'/'
                    #print 'Creating Dir: '+ recursiveDir
                    try:
                            sftp.mkdir(recursiveDir.rstrip('/'))
                    except:
                            continue
    
    #SET ATIME AND MTIME ON SERVER TO LOCAL VALUES
    #MAKES NOT SENSE ATM - sftp.utime(ftphome + '/' + username + '/' + remotePath, tuple( [localStat.st_atime , localStat.st_mtime] ) )
    if writePermission=='rw':
            #owner=sftp.stat( remotePath  )
            #sftp.chown(remotePath.rstrip('/'), owner.st_uid , 500 ) #put "render" as group 
            sftp.chmod(remotePath.rstrip('/'), 0775 ) #give group write permissions to the image folder

    #sftp.close()

def exportVrscene():
    projectPath	 = workspace.getPath()
    sceneName   = os.path.basename(language.Mel.eval('file -q -exn')).rstrip('.mb').rstrip('.ma')
    #oldschool
    #cameraName  = getAttr('vraySettings.batchCamera')
    
    renderLayer = rendering.editRenderLayerGlobals(q=1,crl=1)
    
    vrsceneNameList = []
    
    global localFarm
    cameraList = getRenderableCameras()
    if len( cameraList ) > 1 and localFarm==0:
        #IF WE RENDER MULTI CAMERA WE NEED TO USE EXPORT TO MULTIPLE FILES TO REDUCE UPLOAD OVERHEAD
        global sceneSettings 
        sceneSettings.setAttr ( "vraySettings.misc_separateFiles" , 1 )
        sceneSettings.setAttr ( "vraySettings.misc_exportLights" , 1 )
        sceneSettings.setAttr ( "vraySettings.misc_exportNodes" , 1 )
        sceneSettings.setAttr ( "vraySettings.misc_exportGeometry" , 1 )
        sceneSettings.setAttr ( "vraySettings.misc_exportGeometry" , 1 )
        sceneSettings.setAttr ( "vraySettings.misc_exportGeometry" , 1 )
        sceneSettings.setAttr ( "vraySettings.misc_exportMaterials" , 1 )
        sceneSettings.setAttr ( "vraySettings.misc_exportTextures" , 1 )
        sceneSettings.setAttr ( "vraySettings.misc_exportBitmaps" , 1 )


    #BEI DER ZWEITEN CAM NUR NOCH DIE VRSCENE EXPORTIEREN!!!
    firstCamera = cameraList[0]
    
    for camera in cameraList:
        cameraName = camera.name()
        
        #IF IT'S NOT THE FIRST CAM THEN TURN OFF ALL SEPARATE VRAY FILES
        if camera != firstCamera and localFarm==0:
            sceneSettings.setAttr ( "vraySettings.misc_exportLights" , 0 )
            sceneSettings.setAttr ( "vraySettings.misc_exportNodes" , 0 )
            sceneSettings.setAttr ( "vraySettings.misc_exportGeometry" , 0 )
            sceneSettings.setAttr ( "vraySettings.misc_exportGeometry" , 0 )
            sceneSettings.setAttr ( "vraySettings.misc_exportGeometry" , 0 )
            sceneSettings.setAttr ( "vraySettings.misc_exportMaterials" , 0 )
            sceneSettings.setAttr ( "vraySettings.misc_exportTextures" , 0 )
            sceneSettings.setAttr ( "vraySettings.misc_exportBitmaps" , 0 )
        
        #vrsceneName - before export WITHOUT RENDERLAYER NAME EXTENSION - added at the end - this is because vray append this automatically
        if os.path.exists(projectPath + '/renderScenes') == 0:
            os.makedirs(projectPath + '/renderScenes')
        #vrsceneName = projectPath + '/renderScenes/' + sceneName + '_' + cameraName + '.vrscene'
        vrsceneName = projectPath + '/renderScenes/' + sceneName + '_' + cameraName.replace( ':' , '_' ) + '.vrscene'

        setAttr ("vraySettings.vrscene_filename", vrsceneName)

        #export vrscene
        #language.Mel.eval('vrend')
        language.Mel.eval('renderWindowRenderCamera render "" ' + cameraName);

        #append renderlayername when returning da real name
        vrsceneNameList.append( vrsceneName.replace('.vrscene'  ,   '_' + renderLayer + '.vrscene') )
        
    return vrsceneNameList


def modifyVrscene( filenameList , search , replace , syncFarmObject = syncFarm() ):
    global username
    global ftphome
    cameraList = getRenderableCameras()
    firstCamera = cameraList.pop( 0 ).name().replace( ':' , '_' )
    
    for filename in filenameList:
        readfileObj = open( filename , 'r' )
        
        modifiedFileName = filename.replace( '.vrscene' , '_FBI.vrscene' )
        #ADD THE MODIFIED VRSCENE TO THE UPLOAD_LIST
        syncFarmObject.addFile( modifiedFileName )
        #syncFarmObject.addVrscene( modifiedFileName )
        #TODO CHECK IF FILE EXISTS AND DELETE!!
        writefileObj=open(modifiedFileName,'w')
        
        nextline="init"
        includedFileList = []
        #TODO - REPLACE IDENTICAL INCLUDES WHEN RENDERING MULTIPLE CAMERAS
         
        while nextline!="":
                nextline=readfileObj.readline()
                if nextline.find('img_dir="') > -1  or  nextline.find('auto_save_file="') > -1  and not nextline.find('=""') > -1:
                    img_dir = nextline.split('"')[1]
                    nextline = nextline.replace( img_dir , translatePathToFarm( img_dir ) )
                    writefileObj.write( nextline.replace( '"/home' , '"/remotehome' ) )
                    
                elif nextline.find('img_file="') > -1:
                    writefileObj.write(nextline)
                
                elif nextline.find('file="') > -1 or nextline.find('#include "') > -1:
                    file_path = nextline.split('"')[1]
                    if len(file_path):
                        nextline = nextline.replace( file_path , translatePathToFarm( file_path ) )
                        
                        #IF WE FIND AN INCLUDE FILE THEN WE NEED TO MODIFY THEM LATER AS WELL!!!!
                        if nextline.find('#include "') > -1:
                            
                            nextline = nextline.replace( '.vrscene' , '_FBI.vrscene'  )
                            #file_path = file_path.replace( '.vrscene' , '_FBI.vrscene'  )
                            
                            #IF IT'S NOT THE FIRST CAMERA EXPORT THEN WE NEED TO ADJUST INCLUDE FILES SO THEY INCLUDE ALL SEPARATE EXPORTS FROM THE FIRST CAMERA!!!
                            if nextline.find( firstCamera ) > -1:
                                #ONLY ADD INCLUDES OF FIRST CAM TO THE UPLOAD since the others don't exist
                                includedFileList.append( file_path )
                                print 'NEW INCLUDE: ' + file_path

                            else:
                                for camera in cameraList:
                                    cameraName = camera.name().replace( ':' , '_' )
                                    #print 'DEBUG firstCamera: ' + firstCamera
                                    #print 'DEBUG cameraName: ' + cameraName
                                    #if cameraName != firstCamera:
                                    nextline = nextline.replace( cameraName , firstCamera )
                        else:
                            syncFarmObject.addFile( file_path )
                            
                    writefileObj.write( nextline )
                    
                else:
                    writefileObj.write(nextline.replace(search,replace))
        
        writefileObj.close()
        readfileObj.close()
        
        #NOW MODIFY ALL INCLUDE FILES
        syncFarmObject = modifyVrscene( includedFileList , search , replace , syncFarmObject )
        #remove 
    
    return syncFarmObject

def openParamikoTransport():
    global username
    global key
    global transport
    global sftp

    #TOOO: dropdown in UI um region auszuwaehlen: farm-de , farm-us
    #TODO try: check ob internet da ist
    transport = paramiko.Transport(('farm-de.fullblownimages.com', 22))

    #DONE generate key files! keine passwoerter mehr!!!
    transport.connect(username = username, pkey = key)
    sftp = paramiko.SFTPClient.from_transport(transport)


def closeParamikoTransport():
    global sftp
    sftp.close()
    global transport
    transport.close()
    
def sendCommandViaSSH(command):
    global transport
    if transport==None:
            openParamikoTransport()
    chan=transport.open_session()
    chan.exec_command(command)
    #transport.close()

def getRenderableCameras():
    cameraList=[]
    #print 'Renderable Cameras:'
    for currentCam in ls(type='camera'):
        if getAttr(currentCam+'.renderable'):
            cameraList.append(currentCam.getParent())
    if len(cameraList)==0:
        raise( PopupError('No renderable camera found - please specify at least one') )
    #if len(cameraList)>1:
    #    raise( PopupError('More than one renderable camera found - please specify exactly one') )
    return cameraList

def getOutputImageNameList():
    projectRoot=workspace.getPath()
    try:
            imagePath=workspace.fileRules['images']
    except:
            confirmDialog(message='Maya project set incorrectly!\nYou must specify an "images" directory')
            #changeSceneSettings('restore')
            global sceneSettings
            sceneSettings.reset()
    fileNamePrefix = getAttr('vraySettings.fileNamePrefix')
    
    cameraList = getRenderableCameras()
    
    if fileNamePrefix == None:
        if len( cameraList ) > 1:
            fileNamePrefix='<Layer>/<Camera>/<Scene>'
        else:
            fileNamePrefix='<Layer>/<Scene>'

    #resolve <camera> <layer> and <scene>		
    sceneName   = os.path.basename(language.Mel.eval('file -q -exn'))[:-3]
    fileNamePrefix=fileNamePrefix.replace('<Scene>',sceneName).replace('%s',sceneName)

    currentRenderLayer = editRenderLayerGlobals(q=1,crl=1).replace('defaultRenderLayer','masterLayer')
    #if no <Layer> or %l tag is present we must put renderlayername infront
    #TODO anpassen fuer scenen ohne renderlayer!!!
    if fileNamePrefix.find('<Layer>')>-1 or fileNamePrefix.find('%l')>-1:
            fileNamePrefix=fileNamePrefix.replace('<Layer>',currentRenderLayer).replace('%l',currentRenderLayer)
    else:
            fileNamePrefix=currentRenderLayer + '/' + fileNamePrefix
    
    #put all together
    imagePath=imagePath + '/' + fileNamePrefix
    
    #add projectRoot if imagepath does not contain a : or has a leading / or backslash
    if imagePath.find(':')!=1 and imagePath.find('/')!=0 and imagePath.find('/')!=0:
            imagePath = projectRoot + '/' + imagePath
    
    vrayImageFormatString=getAttr('vraySettings.imageFormatStr')
    if vrayImageFormatString == None:
        vrayImageFormatString ='png'
    extensionArray=vrayImageFormatString.split(' ')
    extension=extensionArray[0]

    #if we have multichannel exr then we must append a DOT
    if len(extensionArray)==2:
            imagePath = imagePath + '.'
    
    padding = getAttr('vraySettings.fileNamePadding')
    #generate nuke-style img name including %04d
    imagePath = imagePath + '%0'+str( padding )+'d.' + extension

    imagePathArray=[]
    for camera in cameraList:
        cameraName = camera.name().replace( ':' , '_' )
        imagePathCamera = imagePath.replace('<Camera>',cameraName).replace('%c',cameraName)
        imagePathArray.append( imagePathCamera )
    
    return imagePathArray
    
def getOutputImageName():
    projectRoot=workspace.getPath()
    try:
            imagePath=workspace.fileRules['images']
    except:
            confirmDialog(message='Maya project set incorrectly!\nYou must specify an "images" directory')
            #changeSceneSettings('restore')
            global sceneSettings
            sceneSettings.reset()
    fileNamePrefix = getAttr('vraySettings.fileNamePrefix')
    
    if fileNamePrefix == None:
        
        fileNamePrefix='<Layer>/<Scene>'

    #resolve <camera> <layer> and <scene>		
    
    #oldschool --> #cameraName=getAttr('vraySettings.batchCamera')
    cameraName = getRenderableCameras()[0].name()
    
    fileNamePrefix=fileNamePrefix.replace('<Camera>',cameraName).replace('%c',cameraName)

    sceneName   = os.path.basename(language.Mel.eval('file -q -exn'))[:-3]
    fileNamePrefix=fileNamePrefix.replace('<Scene>',sceneName).replace('%s',sceneName)

    currentRenderLayer = editRenderLayerGlobals(q=1,crl=1).replace('defaultRenderLayer','masterLayer')
    #if no <Layer> or %l tag is present we must put renderlayername infront
    #TODO anpassen fuer scenen ohne renderlayer!!!
    if fileNamePrefix.find('<Layer>')>-1 or fileNamePrefix.find('%l')>-1:
            fileNamePrefix=fileNamePrefix.replace('<Layer>',currentRenderLayer).replace('%l',currentRenderLayer)
    else:
            fileNamePrefix=currentRenderLayer + '/' + fileNamePrefix
    
    #put all together
    imagePath=imagePath + '/' + fileNamePrefix
    
    #add projectRoot if imagepath does not contain a : or has a leading / or backslash
    if imagePath.find(':')!=1 and imagePath.find('/')!=0 and imagePath.find('/')!=0:
            imagePath = projectRoot + '/' + imagePath
    
    vrayImageFormatString=getAttr('vraySettings.imageFormatStr')
    if vrayImageFormatString == None:
        vrayImageFormatString ='png'
    extensionArray=vrayImageFormatString.split(' ')
    extension=extensionArray[0]

    #if we have multichannel exr then we must append a DOT
    if len(extensionArray)==2:
            imagePath = imagePath + '.'

    padding=''
    for current in range(getAttr('vraySettings.fileNamePadding')):
            padding+='#'

    imagePathArray=[]
    imagePathArray.append(os.path.dirname(imagePath))
    imagePathArray.append(os.path.basename(imagePath))
    imagePathArray.append(padding)
    imagePathArray.append(extension)
    return imagePathArray

def checkPath(path):
    #TODO check ob file innerhalb des projects
    if path.find(' ')>-1:
        raise( PopupError('Illegal path:\n' + path + '\nWhitespaces not allowed!') )


def changeVrayBuild():
    global vrayVersion
    global vrayBuildsMenu
    vrayVersion = int ( optionMenuGrp( vrayBuildsMenu , q=1 , v=1) )
    #print vrayVersion
    
    
def sendAFcommand(vrsceneList, startFrame, endFrame, stepSize, priority, previewFrames):
    global username

    #UI Options -- TODO implement!!
    #renderPreviewFirst=1
    #stepSize = 1
    #priority=50
    #GIonly=0
    #tmpPacketSize=1
    #seqDivMin=1
    #clientGroup='ALL'

    #DONE multi vray versions
    global vrayVersion
    global localFarm
    
    if localFarm==0:
        #get image output directory
        for imagePath in getOutputImageNameList():
            vrayImageDir = os.path.dirname(imagePath)
            #check if the filename matches our convention
            checkPath( vrayImageDir )
            
            #DRY!!!!! DONT REPEAT YOURSELF!!!
            #create image dir on FTP
            #####vrayImageDir = vrayImageDir.replace(':','_COLON_') #need to replace : (colon) with the word "_colon_"
            #TODO - den forward-slash hack fixen
            createDirectoryOnFTP( translatePathToFTP( vrayImageDir ) , 'rw')
            
            #prefix directory with farm paths
            #vrayImageDir = translatePathToFarm( vrayImageDir )

    # Import afanasy python module ( must be in PYTHONPATH).
    import af 
    # Create a job.
    job = af.Job( vrsceneList[0].split( '/' )[-1].rstrip( '.vrscene' ) ) 

    job.setNeedOS('linux')
    job.setPriority(99)
    
    if localFarm==0:
        job.setUserName( username )

    for vrsceneFile in vrsceneList:
        if localFarm==0:
            AFcmd= u'vray_af ' + str( vrayVersion ) + ' ' + translatePathToFarm( vrsceneFile ).replace( '.vrscene' , '_FBI.vrscene' )
        else:
            AFcmd= u'vray_af ' + str( vrayVersion ) + ' ' + vrsceneFile
        #TODO - FIX FOR FLOAT VALUES FOR FRAMES
        AFcmd += ' @#@' #AF WILL SET STARTFRAME HERE
        AFcmd += ' @#@' #AF WILL SET ENDFRAME HERE
        AFcmd += ' ' + str( int( stepSize ) )
        #print AFcmd

        block = af.Block( vrsceneFile , 'vray' ) 
        job.blocks.append(block)
        
        if localFarm==0:
            block.setWorkingDirectory('/home/' + username)
        
        block.setCommand( str( AFcmd ) )
        # Set block tasks preview command arguments.
        #block.setFiles('jpg/img.%04d.jpg') 
        
        # Set block to numeric type, providing first, last frame and frames per host
        block.setNumeric( int(  startFrame ) , int(  endFrame ), 1 , int( stepSize ) )
        #block.tasks = range(13,17) 
        #TODO ein block vorher mit den previewframes
        
    # Send job to Afanasy server.
    result=job.send()     
    return result

def translatePathToFarm(path):
    global username
    homeDir = '/home'
    renderfarmDir='renderfarm'
    #need to replace : (colon) with the word "_colon_"
    translatedPath = homeDir + '/' + username + '/' + renderfarmDir + '/' + path.lstrip('/').replace(':','_COLON_')
    #translatedPath = '/' + path.lstrip('/').replace(':','_COLON_')
    return translatedPath

def translatePathToFTP(path):
    global username
    homeDir = '/home'
    renderfarmDir='renderfarm'
    #need to replace : (colon) with the word "_colon_"
    translatedPath =  '/' + renderfarmDir + '/' + path.rstrip('/').lstrip('/').replace(':','_COLON_')
    #translatedPath = '/' + path.lstrip('/').rstrip('/').replace(':','_COLON_')
    return translatedPath




def assembleRRcommand(vrsceneFile, startFrame, endFrame, stepSize, priority, renderPreviewFirst):

	#UI Options -- TODO implement!!
	#renderPreviewFirst=1
	#stepSize = 1
	#priority=50
	GIonly=0
	tmpPacketSize=1
	seqDivMin=1
	clientGroup='ALL'

	#get image output directory
	vrayImageName = getOutputImageName()
	#check if the filename matches our convention
	checkPath(vrayImageName[0])
	
	#create image dir on FTP
	vrayImageName[0] = vrayImageName[0].replace(':','_COLON_') #need to replace : (colon) with the word "_colon_"
	#TODO - den forward-slash hack fixen
	createDirectoryOnFTP( translatePathToFTP( vrayImageName[0] ) , 'rw')
	
	#prefix directory with farm paths
	vrayImageName[0] = translatePathToFarm( vrayImageName[0] )
	
	
	padding = vrayImageName[2]
	RRext = vrayImageName[3]
	#TODO multi versions
	vrayVersion = '13828'


	RR60cmd = " -NoAutoSceneRead On "
	#TODO - wieder ueberall VRay_StdA mit underscore draus machen
	RR60cmd += " -Software VRayStdA -V " + vrayVersion
	#TODO - LET HOLGER FIX FLOAT VALUES FOR FRAMES
	RR60cmd += " -QS "+ str( int(  startFrame ) )
	RR60cmd += " -QE "+ str( int(  endFrame ) )
	RR60cmd += " -QP " + str( int( stepSize ) )



	RR60layerCmd =  '"' + vrsceneFile + '"' + RR60cmd
	RR60layerCmd += ' -ImageExtention ".'+RRext+'"'
	RR60layerCmd += ' -ImageFramePadding '+str(len(padding))
	RR60layerCmd += ' -ImageDir "' + vrayImageName[0] + '"'

	RR60layerCmd += " -ImageFileName " + vrayImageName[1]

	RR60layerCmd += padding + "." + RRext;

	
	RR60layerCmd += ' "RenderPreview=1~'+str(renderPreviewFirst)+'" "NoFrameChecking=1~'+str(GIonly)+'" "SequenceDivide=1~1" "SequenceDivideMIN=1~'+str(seqDivMin)+'" "SequenceDivideMAX=1~' + str(tmpPacketSize) + '" "MC=1~40" "DCG='+clientGroup+'" "Priority=1~' + str(priority) + '" "AllowLocalSceneCopy=1~0" "AllowLocalRenderOut=1~0" "AllowTextureReplacement=1~0" "PPSequenceCheck=1~0" "PPCreateWebVideo=1~0"'

	RR60layerCmd = '/blackout/ROYAL_RENDER/bin/lx64/rrSubmitterconsole' + ' ' + RR60layerCmd
	return RR60layerCmd
	
def syncWithFarm():
    #collect all files
    #DONE PUT OPTION TO "NOT SYNC" - JUST EXPORT VRSCENE - obolote cause we have a separate button to sync now
    fileList=getAllFilesNeeded()
    #upload - sync project
    
    #DONE CHECK FOR EXISTING FILES
    openParamikoTransport()
    
    if len(fileList):
        uploadFiles(fileList)
    else:
        print "No files to sync"
    
    #finally close remote connection
    closeParamikoTransport()


def submitToCloud( startFloatField , endFloatField , stepFloatField , prioIntField , previewFramesField):
    
    global localFarm
    localFarm=0
    
    startFrame = startFloatField.getValue()
    endFrame = endFloatField.getValue()
    stepSize = stepFloatField.getValue()
    priority = prioIntField.getValue()
    #renderPreviewFirst = renderPreviewCheckBox.getValue()
    previewFrames=startFrame
    
    #DONE SFTP connection offen halten bis alle layer submittet sind,sodass das directory anlegen schneller geht
    #DONE genau hier ein globales SFTPobject erzeugen das erst am ende wieder geschlossen wird
    openParamikoTransport()
    
    global sceneSettings
    sceneSettings=changeSceneSettings()
    
    #set framerange - TODO range per layer - bzw. disable framerange in der GUI und dafuer "use renderglobals settings"
    setAttr( "defaultRenderGlobals.startFrame", startFrame)
    #print startFrame
    setAttr( "defaultRenderGlobals.endFrame", endFrame)
    #print endFrame
    setAttr( "defaultRenderGlobals.byFrameStep", stepSize)	
    #print stepSize
    
    #START EXPORT
    #DO THAT FOR EVERY RENDERLAYER
    #TODO ISOLATE SELECT
    for currentRenderLayer in listConnections('renderLayerManager'):
            if currentRenderLayer.getAttr('renderable'):
                    editRenderLayerGlobals(crl=currentRenderLayer)
                    submitLayerToFarm(startFrame,endFrame,stepSize,priority,previewFrames)
    
    #restore previous scene state
    sceneSettings.reset()

    #finally close remote connection
    closeParamikoTransport()

def submitToFarm( startFloatField , endFloatField , stepFloatField , prioIntField , previewFramesField):
    
    global localFarm
    localFarm=1
    startFrame = startFloatField.getValue()
    endFrame = endFloatField.getValue()
    stepSize = stepFloatField.getValue()
    priority = prioIntField.getValue()
    #renderPreviewFirst = renderPreviewCheckBox.getValue()
    previewFrames=startFrame    
    
    global sceneSettings
    sceneSettings=changeSceneSettings()
    
    #set framerange - TODO range per layer - bzw. disable framerange in der GUI und dafuer "use renderglobals settings"
    setAttr( "defaultRenderGlobals.startFrame", startFrame)
    #print startFrame
    setAttr( "defaultRenderGlobals.endFrame", endFrame)
    #print endFrame
    setAttr( "defaultRenderGlobals.byFrameStep", stepSize)	
    #print stepSize
    
    #START EXPORT
    #DO THAT FOR EVERY RENDERLAYER
    #TODO ISOLATE SELECT
    for currentRenderLayer in listConnections('renderLayerManager'):
            if currentRenderLayer.getAttr('renderable'):
                    editRenderLayerGlobals(crl=currentRenderLayer)
                    submitLayerToFarm(startFrame,endFrame,stepSize,priority,previewFrames)
    
    #restore previous scene state
    sceneSettings.reset() 


class changeSceneSettings():
    def __init__( self ):
        self.initialValues = dict()
        
        #ALWAYS SET AND REMEMBER THESE ATTRs
        self.setAttr( 'defaultRenderGlobals.animation' , 1 )
        self.setAttr( 'vraySettings.animBatchOnly', 0 )
        self.setAttr( 'vraySettings.dontSaveImage', 0 )		
        self.setAttr( 'vraySettings.vrscene_render_on', 0 )		
        self.setAttr( 'vraySettings.vrscene_on', 1 )		
        self.setAttr( 'vraySettings.misc_separateFiles', 0 )		
        self.setAttr( 'vraySettings.misc_meshAsHex', 1 )		
        self.setAttr( 'vraySettings.misc_compressedVrscene', 1 )
        
    def setAttr( self , attrName , value , attrType=None ):
        #TODO - check ob schon im dict
        try:
            self.initialValues[ attrName ] = getAttr( attrName )
            setAttr( attrName , value )
        except:
            self.reset()
            PopupError(attrName + 'not found! It seems that VRAY is not loaded yet or there is no vraySettings node present in your scene!')

        
    def reset( self ):
        for key in self.initialValues:
            setAttr( key , self.initialValues[ key ] )


def changeSceneSettings_OLD(setOrRestore):
	#define gloabl variables to remember their state
	global FBI_animation
	global FBI_animBatchOnly
	global FBI_dontSaveImage
	global FBI_vrscene_render_on
	global FBI_vrscene_on
	global FBI_misc_separateFiles
	global FBI_misc_meshAsHex
	global FBI_misc_compressedVrscene


	try:
		if setOrRestore=="set":
			FBI_animation = getAttr( "defaultRenderGlobals.animation")
			setAttr( "defaultRenderGlobals.animation", 1)
			FBI_animBatchOnly = getAttr("vraySettings.animBatchOnly")
			setAttr( "vraySettings.animBatchOnly", 0)

			FBI_dontSaveImage = getAttr ("vraySettings.dontSaveImage")
			setAttr ("vraySettings.dontSaveImage",0)
			FBI_vrscene_render_on = getAttr ("vraySettings.vrscene_render_on")
			setAttr ("vraySettings.vrscene_render_on",0)
			FBI_vrscene_on = getAttr ("vraySettings.vrscene_on")
			setAttr ("vraySettings.vrscene_on",1)
			FBI_misc_separateFiles = getAttr ("vraySettings.misc_separateFiles")
			setAttr ("vraySettings.misc_separateFiles",0)
			FBI_misc_meshAsHex = getAttr ("vraySettings.misc_meshAsHex")
			setAttr ("vraySettings.misc_meshAsHex",1)
			FBI_misc_compressedVrscene = getAttr ("vraySettings.misc_compressedVrscene")
			setAttr ("vraySettings.misc_compressedVrscene",1)
			
		if setOrRestore=="restore":
			setAttr( "defaultRenderGlobals.animation", FBI_animation)
			setAttr( "vraySettings.animBatchOnly", FBI_animBatchOnly)
			
			setAttr ("vraySettings.dontSaveImage", FBI_dontSaveImage)		
			setAttr ("vraySettings.vrscene_render_on", FBI_vrscene_render_on)		
			setAttr ("vraySettings.vrscene_on", FBI_vrscene_on)		
			setAttr ("vraySettings.misc_separateFiles", FBI_misc_separateFiles)		
			setAttr ("vraySettings.misc_meshAsHex", FBI_misc_meshAsHex)		
			setAttr ("vraySettings.misc_compressedVrscene", FBI_misc_compressedVrscene)
			
			#END PROGRESS BAR - just in case
			progressBar(gMainProgressBar, edit=True, endProgress=True)
	except:
		PopupError('It seems that VRAY is not loaded yet or there is no vraySettings node present in your scene!')
	
	
def submitLayerToFarm(startFrame,endFrame,stepSize,priority,previewFrames ):
    global username
            
    #EXPORT and MODIFY VRSCENE HERE
    projectPath	 = workspace.getPath()
    
    
    vrsceneList = exportVrscene()
    
    global localFarm
    if localFarm==0:
        vrsceneAndDependencies = modifyVrscene( vrsceneList , projectPath , translatePathToFarm( projectPath ) )
    
        #UPLOAD vrscene AND ALL NEEDED FILES!!!
        #TODO auslagern auf nachdem alle renderlayer submitted sind!!!
        #vrscene = vrsceneAndDependencies.fileList[0]
        
        vrsceneAndDependencies.upload()
        
    #print 'DEBUG vrscene' + vrscene
    #bend vrscene name over to farm path
    ###vrscene = translatePathToFarm( vrscene )
    #print 'DEBUG vrscene' + vrscene
    
    sendAFcommand( vrsceneList , startFrame, endFrame, stepSize, priority, previewFrames )
    
    if localFarm==0:
        vrsceneAndDependencies.clear()
    #TODO enable logfile
    #sendCommandViaSSH(RRcommand)

def setCurrentFrame(startFloatField,endFloatField):
	startFloatField.setValue(currentTime(q=1))
	endFloatField.setValue(currentTime(q=1))

def setTimeline(startFloatField,endFloatField):
	startFloatField.setValue(playbackOptions(q=1,min=1))
	endFloatField.setValue(playbackOptions(q=1,max=1))
	
def buildUI_2010():

    winWidth=500
    winHeigth=110
    global farmSubmitterWin
    try:
            farmSubmitterWin.delete()
    except:
                    pass
    farmSubmitterWin = window(title="FBI_farmSubmitter by www.fullblownimages.com", rtf = 1,w=winWidth,h=winHeigth)
    #farmSubmitterScrollLayout = scrollLayout(childResizable = 1)

    farmSubmitterFormLayout = formLayout(w=winWidth-20)
    #define first row
    rangeText = text(label='FrameRange')
    formLayout(farmSubmitterFormLayout, edit = True,  attachForm=[(rangeText , 'left', 5), (rangeText , 'top', 6)])
    
    startFloatField = floatField(v=getAttr("defaultRenderGlobals.startFrame") , pre=1)
    formLayout(farmSubmitterFormLayout, edit = True,  attachForm=[(startFloatField , 'top', 2)],  attachControl=[(startFloatField, 'left', 5, rangeText)])

    endFloatField = floatField(v=getAttr("defaultRenderGlobals.endFrame") , pre=1)
    formLayout(farmSubmitterFormLayout, edit = True,  attachForm=[(endFloatField, 'top', 2)],  attachControl=[(endFloatField, 'left', 5, startFloatField )])

    stepFloatField = floatField(v=getAttr("defaultRenderGlobals.byFrameStep") , pre=1)
    formLayout(farmSubmitterFormLayout, edit = True,  attachForm=[(stepFloatField, 'top', 2)],  attachControl=[(stepFloatField, 'left', 5, endFloatField )])

    currentFrameButton = button(label='current frame', c = Callback(setCurrentFrame , startFloatField , endFloatField) )
    formLayout(farmSubmitterFormLayout, edit = True,  attachForm=[(currentFrameButton, 'top', 0)],  attachControl=[(currentFrameButton, 'left', 5, stepFloatField)])
    #print startFloatField

    timeLineButton = button(label='timeline', c = Callback(setTimeline , startFloatField , endFloatField) )
    formLayout(farmSubmitterFormLayout, edit = True,  attachForm=[(timeLineButton , 'top', 0),  (timeLineButton, 'right', 0)],  attachControl=[(timeLineButton , 'left', 5, currentFrameButton)])

    startText = text(label='startFrame')
    formLayout(farmSubmitterFormLayout, edit = True,  attachControl=[(startText, 'left', 5, rangeText) , (startText, 'top', 5, startFloatField) , (startText, 'right', 5, endFloatField) ])

    endText = text(label='endFrame')
    formLayout(farmSubmitterFormLayout, edit = True,  attachControl=[(endText, 'left', 5, startText), (endText, 'top', 5, startFloatField) , (endText, 'right', 5, stepFloatField)  ])

    stepText = text(label='stepSize')
    formLayout(farmSubmitterFormLayout, edit = True,  attachControl=[(stepText, 'left', 5, endText), (stepText, 'top', 5, startFloatField) , (stepText, 'right', 5, currentFrameButton)  ])

    previewImagesText = text(label='Preview Images (comma separated)')
    formLayout(farmSubmitterFormLayout, edit = True,  attachForm=[(previewImagesText , 'left', 5) ], attachControl=[ (previewImagesText, 'top', 5, startText) ])
    
    previewImagesTextField = textField(en=0)
    formLayout(farmSubmitterFormLayout, edit = True,  attachControl=[ (previewImagesTextField, 'top', 5, startText) , (previewImagesTextField, 'left', 5, previewImagesText) , (previewImagesTextField, 'right', 5, timeLineButton) ])

    #-------------------------------------------------------------------
    sepLine1 = separator()
    formLayout(farmSubmitterFormLayout, edit = True,  attachForm=[(sepLine1 , 'left', 0),  (sepLine1, 'right', 0)], attachControl=[ (sepLine1, 'top', 5, previewImagesText) ])

    prioText = text(label='Priority')
    formLayout(farmSubmitterFormLayout, edit = True,  attachForm=[(prioText   , 'left', 5)], attachControl=[ (prioText  , 'top', 8, sepLine1) ])

    prioIntField = intField(v=50)
    formLayout(farmSubmitterFormLayout, edit = True,  attachControl=[ (prioIntField , 'left', 0, rangeText) , (prioIntField, 'top', 5, sepLine1) , (prioIntField , 'right', 0, endText)])

    #renderPreviewCheckBox = checkBox(l='render preview first',v=1)
    #formLayout(farmSubmitterFormLayout, edit = True,  attachControl=[ (renderPreviewCheckBox  , 'right', 0, currentFrameButton) , (renderPreviewCheckBox , 'top', 5, sepLine1) ])
    #TODO - get supported version vie http 
    global vrayBuildsMenu
    vrayBuildsMenu = optionMenuGrp(label='V-Ray Version' , cc = Callback( changeVrayBuild ) )
    global vrayVersion
    #TODO - get vray version from ENV VAR $VRAY_VERSION
    vrayVersion=20004 
    menuItem( label='20004' )
    menuItem( label='22001' )
    menuItem( label='18822' )
    menuItem( label='15001' )
    menuItem( label='15000' )
    formLayout(farmSubmitterFormLayout, edit = True,  attachControl=[ (vrayBuildsMenu  , 'left', 5, prioIntField) , (vrayBuildsMenu  , 'right', 0, timeLineButton) , (vrayBuildsMenu , 'top', 5, sepLine1) ])

    #syncButton = button(l='SYNC ALL NEEDED FILES WITH FARM' , bgc=[1, 1, 0.5] , c=Callback(syncWithFarm) )
    #formLayout(farmSubmitterFormLayout, edit = True,  attachForm=[(syncButton , 'left', 0),  (syncButton, 'right', 0)], attachControl=[ (syncButton, 'top', 5, prioIntField) ])

    submitButton = button(l='SUBMIT RENDERLAYERS TO FARM' , bgc=[0.5, 1, 0.5] , c=Callback( submitToCloud, startFloatField , endFloatField , stepFloatField , prioIntField , 1 ) )
    formLayout(farmSubmitterFormLayout, edit = True,  attachForm=[(submitButton , 'left', 0),  (submitButton, 'right', 0)], attachControl=[ (submitButton, 'top', 5, prioIntField) ])

    #-------------------------------------------------------------------
    sepLine2 = separator()
    formLayout(farmSubmitterFormLayout, edit = True,  attachForm=[(sepLine2 , 'left', 0),  (sepLine2, 'right', 0)], attachControl=[ (sepLine2, 'top', 5, submitButton) ])
    
    estimateText = text(label='Estimated cost =')
    formLayout(farmSubmitterFormLayout, edit = True,  attachForm=[(estimateText , 'left', 5) ], attachControl=[ (estimateText, 'top', 5, sepLine2) ])
    
    benchScore = floatField(v=1.0 , pre=1)
    formLayout(farmSubmitterFormLayout, edit = True,  attachControl=[(benchScore, 'left', 5, estimateText) , (benchScore, 'top', 1, sepLine2)])

    

    farmSubmitterWin.show()

def buildUI():
    if versions.current() > versions.v2010:
        buildUI_2011()
    else:
        buildUI_2010()

def buildUI_2011():
    
    winWidth=550
    winHeigth=200
    global farmSubmitterWin
    try:
            farmSubmitterWin.delete()
    except:
            pass

    with window(title="FBI_farmSubmitter by www.fullblownimages.com", rtf = 1,w=winWidth,h=winHeigth) as farmSubmitterWin:
        with scrollLayout():
            with frameLayout(collapsable=True , collapse = False , label='Submit' , w=525):
                with rowColumnLayout( numberOfColumns=6, columnWidth=[(1, 100), (2, 80), (3, 80), (4, 60), (5, 100), (6, 100)] ):
                    text(label='FrameRange')
                    startFloatField = floatField(v=getAttr("defaultRenderGlobals.startFrame") , pre=1)
                    endFloatField = floatField(v=getAttr("defaultRenderGlobals.endFrame") , pre=1)
                    stepFloatField = floatField(v=getAttr("defaultRenderGlobals.byFrameStep") , pre=1)
                    currentFrameButton = button(label='current frame', c = Callback(setCurrentFrame , startFloatField , endFloatField) )
                    timeLineButton = button(label='set to timeline', c = Callback(setTimeline , startFloatField , endFloatField) )

                    text(label='')
                    text(label='startFrame')
                    text(label='endFrame')
                    text(label='stepSize')
                    #text(label='')    
                    #text(label='')
                with rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 100), (2, 160), (3, 200)] ): 
                    text(label='Previewframes' , en=0 )
                    previewImagesTextField = textField( en=0 )
                    text(align='left' , label=' (comma separated list)')
                    
                #with columnLayout():
                separator()
                
                with rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 100), (2, 30), (3, 250)] ):
                    text(label='Priority')
                    prioIntField = intField(v=50)
                    #renderPreviewCheckBox = checkBox(l='render preview first',v=1)
                    
                    #TODO - get supported version vie http 
                    global vrayBuildsMenu
                    vrayBuildsMenu = optionMenuGrp(label='V-Ray Version' , cc = Callback( changeVrayBuild ) )
                    #vrayBuildsMenu = optionMenuGrp(
                    global vrayVersion
                    vrayVersion=18323
                    menuItem( label='18323' )
                    menuItem( label='20004' )
                    menuItem( label='22001' )
                    menuItem( label='18822' )
                    menuItem( label='15001' )
                    menuItem( label='15000' )
                
                #with rowColumnLayout( numberOfColumns=2, columnWidth=[ (1, 260), (2, 260) ] ):
                with rowColumnLayout( numberOfColumns=1, columnWidth=[ (1, 520) ] ):
                    #syncButton = button(l='SYNC ALL NEEDED FILES WITH FARM' , bgc=[1, 1, 0.5] , c=Callback(syncWithFarm) )
                    submitButton = button(l='SUBMIT RENDERLAYERS TO CLOUD' , bgc=[0.5, 1, 0.5] , c=Callback( submitToCloud, startFloatField , endFloatField , stepFloatField , prioIntField , 1 ) )
                    submitButton = button(l='SUBMIT RENDERLAYERS TO FARM' , bgc=[0.5, 1, 0.5] , c=Callback( submitToFarm, startFloatField , endFloatField , stepFloatField , prioIntField , 1 ) )
            with frameLayout(collapsable=True , collapse = True , label='Cost Estimator' , w=525):
                with rowColumnLayout( numberOfColumns=8, columnWidth=[(1, 100), (2, 30), (3, 20), (4, 30), (5, 40) , (6, 40), (7, 40), (8, 220)] ):
                    text('avrg. rendertime')
                    rendertime_h = intField(v=0 )
                    text('h')
                    rendertime_m = intField(v=1 )
                    text('min')
                    rendertime_s = intField(v=0 )
                    text('sec')
                    text(' (on this machine)' , align='left')
                with rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 100), (2, 60)] ):    
                    text('Benchmark Score')
                    benchScore = floatField(v=1.0 , pre=1)
                    text(' (of this machine)' , align='left')
                    
    farmSubmitterWin.show()
