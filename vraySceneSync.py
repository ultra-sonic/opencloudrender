import s3IO , re
def uploadWithDependencies( bucket_name , vrscene_list ):
    for vrscene_path in vrscene_list:
        for asset in getDependencies( vrscene_path ):
            s3IO.upload_file( bucket_name , asset )
        s3IO.upload_file( bucket_name , vrscene_path )

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

    return assets