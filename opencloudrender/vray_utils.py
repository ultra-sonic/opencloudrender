import os
from path_utils import validate_file_path


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
                    vray_settings_dict[ key ] = value
                if line.find('}') > -1:
                    return vray_settings_dict
    raise "No Vray Settings found"

def get_vrscene_data_tuple( vrscene_path ):
    vray_settings = get_vray_settings( vrscene_path )
    return ( os.path.basename( vrscene_path ) , vray_settings['anim_start'] , vray_settings['anim_end'] , 'cam TDB' , vrscene_path )


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

"""
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
"""