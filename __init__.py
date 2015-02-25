import fb_vrayRepoSync , fb_vraySceneSync , fb_afanasySubmit

vray_repo_bucket_name   = 'vray-repo'               # TODO goes into UI
vrscene_bucket_name     = 'fbcloudrender-testdata'  # TODO goes into UI

def showUI():
    pass

def test():
    fb_vrayRepoSync.push( vray_repo_bucket_name )

    vrscene_list = [ '/blackout/volume1/DEFAULT_PROJECT/04_CGI/_workarea/omarkowski/MAYA/cloudtest_v001.vrscene' ]
    fb_vraySceneSync.uploadWithDependencies( vrscene_bucket_name , vrscene_list )

    start_frame = 1
    end_frame   = 1
    step_size   = 1
    priority    = 99

    #fb_afanasySubmit.sendJob(  vrscene_list, start_frame, end_frame, step_size, priority )


test()
