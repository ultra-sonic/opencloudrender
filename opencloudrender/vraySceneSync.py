from PySide import QtCore
import s3IO , re
def uploadWithDependencies( bucket_name , vrscene_path , update_progress_signal=QtCore.Signal() ):
    print "Start syncing assets..."
    ret = 0
    progress_current = 0
    dependencies = getDependencies( vrscene_path )
    progress_100 = len( dependencies )+1

    for asset in dependencies:
        if s3IO.upload_file( bucket_name , asset ) != 0:
            ret=1
        progress_current=progress_current+1
        update_progress_signal.emit( asset , progress_current , progress_100 )

    update_progress_signal.emit( vrscene_path , 99 , 100 )
    if s3IO.upload_file( bucket_name , vrscene_path ) != 0:
        ret=1
    update_progress_signal.emit( "Done syncing assets..." , 100 , 100 )
    return ret

def getDependencies( vrscene_path ):
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
        assets.extend( getDependencies( included_scene ) )

    assets.extend( included_vrscenes )
    return assets