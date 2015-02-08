import os
from pymel.core import *
import sys
import shutil
import urllib
import zipfile
#TODO
#site-packages 
class install():

    def __init__( self ):
        #init variables
        self.tempdir = tempdir = os.environ['TMP']
        self.fileList = [ 'pycrypto-2.5.zip' , 'paramiko-1.7.7.1.zip' , 'FBI_farmSubmitter.zip' ]
        self.cleanFileList = [ 'FBI_farmSubmitter.pyc' ]
        for current in self.fileList:
            self.cleanFileList.append(current)
        self.cleanDirList = [ 'pycrypto-2.5' , 'paramiko-1.7.7.1' , 'FBI_farmSubmitter' ]
        
        #first cleanup - in case last installer quit unexpectedly
        self.cleanUp( mode='quiet' )
        
        self.download(  )
        self.do()
        
        #second cleanup
        self.cleanUp(  )
        
        #TBD
        self.addToShelf()
        
    def addToShelf( self ):
        pass
    
    def cleanUp( self  , mode='verbose'):
        print 'Cleaning up...\n'
        for file in self.cleanFileList:
            localFileName = self.tempdir + '/' + file
            try:
                os.remove( localFileName )
            except:
                if mode=='verbose':
                    print 'Error: Could not remove file: ' + localFileName
                
        for dirName in self.cleanDirList:
            localDirName = self.tempdir + '/' + dirName
            try:
                shutil.rmtree( localDirName )
            except:
                if mode=='verbose':
                    print 'Warning: Could not remove dir:  ' + localDirName
        
        
    def download( self  ):
        print 'Downloading files...\n'
        #DOWNLOAD
        ftp_root = 'http://rndr.fllblwn.com/DEPLOY/'
        for file in self.fileList:
            url = ftp_root + file
            try:                
                webFile = urllib.urlopen( url )
            except:
                PopupError( 'Could not connect to:\n' + url + '\nPlease check you internet connection!')
            localFileName = self.tempdir + '/' + file
            localFile = open( localFileName , 'w')
            localFile.write( webFile.read() )
            webFile.close()
            localFile.close()
            
            #UNZIP
            myzip = zipfile.ZipFile(localFileName, 'r')
            myzip.extractall( self.tempdir )
            #CLEANUP
        print 'Download finished...\n'
        
    def buildUI( self ):
        winWidth=550
        winHeigth=50
        global FBI_installWin
        try:
                FBI_installWin.delete()
        except:
                pass

        with window(title="FBI Installer", rtf = 1,w=winWidth,h=winHeigth) as FBI_installWin:
            with columnLayout():
                #TODO split depending on OS
                self.installLoc = optionMenuGrp(label='Install location:' )
                menuItem( label = 'DEFAULT MAYA INSTALLDIR' )
                for path in os.environ['MAYA_SCRIPT_PATH'].split(';'):
                    menuItem( label = path )
                
                installButton = button(l='INSTALL FBI_farmSubmitter' , c = Callback( self.do ) , w = winWidth , bgc=[0.5, 1, 0.5] )
        FBI_installWin.show()
        button( installButton , e = 1 , w = FBI_installWin.getWidth() )

    def update( self ):
        ##AUSLAGERN DIRKET IN farmSubmitter 
        pass
    

    def do( self ):
        
        #installLocation = self.installLoc.getValue()
        installLocation = 'DEFAULT MAYA INSTALLDIR'
        
        
        #mayapy = 'cmd /k ' + os.environ['MAYA_LOCATION'] + '/bin/mayapy'
        mayapy = '"' + os.environ['MAYA_LOCATION'] + '/bin/mayapy"'
        
        #scriptLocation = os.path.dirname( __file__ )
        scriptLocation = self.tempdir
        
        if installLocation == 'DEFAULT MAYA INSTALLDIR':
            prefix = ''
            for path in os.environ['MAYA_SCRIPT_PATH'].split(';'):
                if path.find( os.environ['HOME'] ) > -1   and path.find( '20' ) > -1:
                    installLocation = path
                    print 'NEW INSTALL LOC: ' + installLocation
                    break

        else:
            prefix = ' --prefix "' + installLocation + '"'
        
        print 'Script: ' + scriptLocation
        print 'Prefix: ' + prefix
        print 'Mayapy: ' + mayapy
        print 'Installing to:' + installLocation
        
        installCmd = mayapy + ' setup.py install' + prefix
        print installCmd
        #INSTALL PYCRYPTO
        os.chdir( scriptLocation + '/pycrypto-2.5' )
        os.system( installCmd + ' --skip-build')
        #INSTALL PARAMIKO
        os.chdir( scriptLocation + '/paramiko-1.7.7.1' )
        os.system( installCmd )
        #TODO - DELETE crypto and paramiko
             
        #COPY ALL OTHER STUFF TO installLocation OR TO MAYA-SCRIPT-DIR IN USER HOME
        try:
            shutil.rmtree( installLocation + '/FBI_farmSubmitter' )
        except:
            pass
        shutil.copytree( scriptLocation + '/FBI_farmSubmitter' ,  installLocation + '/FBI_farmSubmitter' )
        shutil.copy( scriptLocation + '/FBI_farmSubmitter.pyc' ,  installLocation )
        
        print "Ok...seems like a pretty successful install...now let's rock some renders..."
        print "Just put the following lines inside one of your script editors python tabs:"
        print "import FBI_farmSubmitter"
        print "FBI_farmSubmitter.buidlUI()"
        
        
        
         
        