# Import afanasy python module ( must be in PYTHONPATH).
import logging
from PySide import QtCore
import os , af
from pathUtils import validate_file_path
from vrayUtils import get_vray_settings

def sendToAfanasy( vrscene_path , step_size=1 , start_frame_override = -1 , end_frame_override = -1 , priority=99 , preview_frames=False , vray_release_type="official" , vray_build="24002" , host_application="Maya" , host_application_version="2015" ):
    logging.info( "Start sending job to server..." )
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

    logging.debug( "AFcmd: " + AFcmd )

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
    result=job.send( verbose=True )
    logging.debug( "Result: " + str(result) )
    if result[0]:
        logging.info( "Finished sending job to server..." )
        return True
    else:
        logging.error( "Failed sending job to server..." )
        return False

class SubmitScenesThread(QtCore.QThread):
    # thx to those guys i mad threading work ;)
    # http://stackoverflow.com/questions/20657753/python-pyside-and-progress-bar-threading
    # http://www.matteomattei.com/pyside-signals-and-slots-with-qthread-example/

    update_progress_signal = QtCore.Signal( str , int , int ) #create a custom signal we can subscribe to to emit update commands

    def __init__(self, parent=None ):
        super(SubmitScenesThread,self).__init__(parent)
        self.exiting = False
        self.data_list = parent.data_list
        self.renderer_version = parent.ui.vrayVersionComboBox.currentText()

    def run(self):
        prog=0
        prog_max=len(self.data_list)
        for scene in self.data_list:
            if self.exiting==False:
                if scene[4]==True and scene[5]==True: #check if submit and sync is True
                    self.update_progress_signal.emit( 'sending job: ' + scene[0] , prog , prog_max )
                    if sendToAfanasy( scene[0] , priority=50 , vray_build=self.renderer_version )==False:
                        self.update_progress_signal.emit( 'error sending: ' + scene[0] + ' - aborting', prog , prog_max )
                        return
            else:
                self.update_progress_signal.emit( 'canceled sending of: ' + scene[0] , prog , prog_max )
            prog=prog+1
        self.update_progress_signal.emit( 'submission of ' + str(prog_max) + ' jobs done! ' , prog , prog_max )


    @QtCore.Slot()
    def cancel(self):
        self.exiting = True
