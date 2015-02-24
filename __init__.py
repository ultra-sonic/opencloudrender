import fb_vrayRepoSync , fb_vraySceneSync

vray_repo_bucket_name   = 'vray-repo'               # TODO goes into UI
vrscene_bucket_name     = 'fbcloudrender-testdata'  # TODO goes into UI

def showUI():
    pass

def test():
    fb_vrayRepoSync.push( vray_repo_bucket_name )
    vrscene_list = [ '/blackout/volume1/DEFAULT_PROJECT/04_CGI/_workarea/omarkowski/MAYA/cloudtest_v001.vrscene' ]
    fb_vraySceneSync.uploadWithDependencies( vrscene_bucket_name , vrscene_list )

test()
