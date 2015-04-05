import os , re
from pathUtils import validate_file_path


def get_vray_settings( vrscene_path ):
    print "DEBUG - reading vrscene: " + os.path.basename( vrscene_path )
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
                    return vray_settings_dict
    raise KeyError("No Vray Settings found")

def get_vrscene_data( vrscene_path ):
    vray_settings = get_vray_settings( vrscene_path )
    default_camera = get_default_camera( vrscene_path )
    #return ( os.path.basename( vrscene_path ) , vray_settings['anim_start'] , vray_settings['anim_end'] , 'cam TDB' , vrscene_path )
    return [ vrscene_path , vray_settings['anim_start'] , vray_settings['anim_end'] , default_camera , True , False ]


def get_default_camera( vrscene_path ):
    with open( vrscene_path , 'r' ) as vrscene:
        for line in vrscene:
            if line.startswith('CameraDefault '):
                default_camera = line.split(' ')[1]
                return default_camera
    raise Exception("No anim_frame_padding found in vrscene" + vrscene_path )


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

def getVrsceneDependencies( vrscene_path ):
    asset_patterns=[' file=".*"']
    included_vrscenes = []
    assets = []
    with open( vrscene_path , 'r' ) as vrscene:
        for line in vrscene:
            if line.startswith('#include') and line.find('.vrscene'):
                included_vrscenes.append( line.split('"')[1] )
            for pattern in asset_patterns:
                regex = re.compile( pattern )
                match = regex.search( line )
                if match != None:
                    file_path = line[ match.start() + pattern.find('"') + 1 : match.end()-1  ]
                    if file_path != '':
                        assets.append( file_path )

    #recurse into included vrscenes
    for included_scene in included_vrscenes:
        #print "recursing into: " + included_scene
        assets.extend( getVrsceneDependencies( included_scene ) )

    assets.extend( included_vrscenes )
    return assets