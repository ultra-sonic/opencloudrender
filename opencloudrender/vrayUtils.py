import logging
import os , re , zipfile
from pathUtils import validate_file_path
from PySide import QtGui,QtCore


def get_full_path( file_name , current_dir ):
    full_file_path = file_name
    if os.path.isfile( full_file_path ) == False:
        full_file_path = os.path.join( current_dir , file_name )
        if os.path.isfile( full_file_path ):
            return full_file_path
        else:
            msg='Include file not found: ' + file_name
            logging.error( msg )
            raise Exception( msg )

def get_full_image_dir_path( img_dir , current_dir):
    if img_dir.startswith('.'):
        full_path=os.path.abspath( os.path.join( current_dir , img_dir )  )
        logging.info( 'convert: {0} to absolute path: {1}'.format( img_dir , full_path ))
        return full_path
    else:
        return img_dir

def get_vray_settings( vrscene_path ):
    logging.debug( "Reading vrscene: " + os.path.basename( vrscene_path ) )
    vray_settings_dict={}
    vray_settings_output_found=False
    with open( vrscene_path , 'r' ) as vrscene:
        for line in vrscene:
            if line.find('SettingsOutput vraySettingsOutput {') > -1:
                vray_settings_output_found=True
            if vray_settings_output_found:
                stripped_line=line.lstrip()
                equals_sign_pos = stripped_line.find('=')
                semi_colon_pos = stripped_line.find(';')
                if equals_sign_pos > -1 and semi_colon_pos > -1:
                    key   = stripped_line[ : equals_sign_pos ]
                    value = stripped_line[ equals_sign_pos+1 : semi_colon_pos ]
                    vray_settings_dict[ key ] = value.lstrip('"').rstrip('"')
                if line.find('}') > -1:
                    # ensure full-path in img_dir
                    vray_settings_dict['img_dir']=get_full_image_dir_path( vray_settings_dict['img_dir'] , os.path.dirname( vrscene_path ))
                    return vray_settings_dict
    error_msg="No Vray Settings found"
    logging.error( error_msg )
    raise KeyError( error_msg )

def get_vrscene_data( vrscene_path ):
    logging.debug('get_vrscene_data: ' + vrscene_path )
    vray_settings = get_vray_settings( vrscene_path )
    default_camera = get_default_camera( vrscene_path )
    #return ( os.path.basename( vrscene_path ) , vray_settings['anim_start'] , vray_settings['anim_end'] , 'cam TDB' , vrscene_path )
    ret_val= [ vrscene_path , vray_settings['anim_start'] , vray_settings['anim_end'] , default_camera , True , False ]
    logging.debug( ret_val )
    return ret_val


def get_default_camera( vrscene_path ):
    with open( vrscene_path , 'r' ) as vrscene:
        for line in vrscene:
            if line.startswith('CameraDefault '):
                default_camera = line.split(' ')[1]
                return default_camera
    logging.warning("No default camera found in vrscene - are you using a custom lens shader" + vrscene_path )
    return 'not found - maybe custom lens-shader'


def get_output_image_path( vrscene_path ):
    print "OBSOLETE FUNCTION - use get_vray_settings instead"
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

def get_vrscene_dependencies( vrscene_path , recursion_depth=0 ):
    logging.debug('get_vrscene_dependencies: ' + vrscene_path )
    logging.debug('recursion_depth: ' + str(recursion_depth ) )
    asset_patterns=[' file=".*"']
    included_vrscenes = []
    assets = []
    with open( vrscene_path , 'r' ) as vrscene:
        for line in vrscene:
            if line.startswith('#include') and line.find('.vrscene'):
                included_scene = line.split('"')[1]
                included_vrscenes.append( get_full_path( included_scene , os.path.dirname(vrscene_path) ) )

            for pattern in asset_patterns:
                regex = re.compile( pattern )
                match = regex.search( line )
                if match != None:
                    file_path = line[ match.start() + pattern.find('"') + 1 : match.end()-1  ]
                    if file_path != '':
                        assets.append( file_path )

    #recurse into included vrscenes
    for included_scene in included_vrscenes:
        #check for relative include paths if file does not exist
        assets.extend( get_vrscene_dependencies( included_scene , recursion_depth=recursion_depth+1) )

    assets.extend( included_vrscenes )
    logging.debug( assets )
    return assets

def findInNamelist( search_string , name_list ):
    for item in name_list:
        if item.find(search_string) > -1:
            return True
    return False

class InstallFromZipThread(QtCore.QThread):
    show_error_signal = QtCore.Signal( str )

    def __init__( self , zip_file_path , install_root_dir , parent=None):
        super(InstallFromZipThread,self).__init__()
        self.zip_file_path = zip_file_path
        self.install_root_dir = install_root_dir
        self.parent = parent

    def run(self):
        # validate zip contents
        zip_file = zipfile.ZipFile( self.zip_file_path )
        #print zip_file.namelist()
        if findInNamelist( 'vray.bin' , zip_file.namelist() ) == False:
            self.show_error_signal.emit( 'vray.bin not found inside zip file!' )
            return False

        # find build revision number
        regex = re.compile( '_[0-9][0-9][0-9][0-9][0-9]_' )
        build_revision_match = regex.search( os.path.basename( self.zip_file_path ) )
        if build_revision_match != None:
            build_revision = build_revision_match.group().strip('_')
            print build_revision
        else:
            self.show_error_signal.emit( 'No 5 digit revision number found!' )
            return False

        # extract
        install_dir = os.path.join( self.install_root_dir , build_revision )
        if os.path.isdir(install_dir):
            self.show_error_signal.emit( 'Directory {0} already exists!'.format(install_dir) )
            return False
        else:
            os.makedirs( install_dir ) # todo check mode
            zip_file.extractall( install_dir )
            return True