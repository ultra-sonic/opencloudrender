from PySide import QtCore
import boto
import boto.s3
import hashlib

import os
import sys
from pathUtils import strip_file_path

# max size in bytes before uploading in parts. between 1 and 5 GB recommended
MAX_SIZE = 20 * 1000 * 1000
#size of parts when uploading in parts
PART_SIZE = 6 * 1000 * 1000

try:
    conn = boto.connect_s3()
except boto.exception.NoAuthHandlerFound:
    print 'No s3 credentials found - you cannot submit!'

existing_buckets=dict()


def create_bucket( bucket_name ):
    try:
        bucket = conn.create_bucket(bucket_name,
                                location=boto.s3.connection.Location.EU)
        return bucket
    except boto.exception.S3ResponseError as e:
        raise e('Seems you habe no permission to create a bucket!')


def get_bucket( bucket_name , auto_create=False , parent=None ):
    if bucket_name not in existing_buckets.keys():
        try:
            bucket = conn.get_bucket(bucket_name)
        except boto.exception.S3ResponseError as e:
            print 'Bucket "' + bucket_name + '" does not exist or you have no permission!'
            if parent!=None:
                # todo present Qt confirmdialog and override auto_create based in decision
                auto_create=True
            if auto_create:
                print "trying to create it now!"
                bucket = create_bucket( bucket_name )
            else:
                raise e('User decided not to create the bucket. Raising exception now!')
        existing_buckets[ bucket_name ] = bucket
        return bucket
    else:
        return existing_buckets[ bucket_name ]



def get_files_in_directory(source_dir , recursive=False ):
    uploadFileNames = []
    for (source_dir, dirname, filename) in os.walk( source_dir ):
        uploadFileNames.extend(filename)
    return uploadFileNames


def percent_cb(complete, total):
    sys.stdout.write( "progress {0} / {1}\r".format( complete , total ))
    sys.stdout.flush()

def download_files(data_bucket_name, frame_list , update_progress_signal=QtCore.Signal ):
    bucket=get_bucket( data_bucket_name ) # todo implement a get_bucket function
    dir_name=os.path.dirname( frame_list[0] ).lstrip('/')
    bucket_list = bucket.list( prefix=dir_name )
    download_frame_dict = {}
    for object in bucket_list:
        keyString = '/' + str(object.key)
        #if keyString.endswith('exr'):
        #    print("Found exr: " + keyString )
        doubleDashKeyString = os.path.normpath( '/' + keyString ) # this is just a workaround for stupid windoze to write to the network share - should have no effect on Linux and OSX
        if keyString in frame_list:
            download_frame_dict[ doubleDashKeyString ]=object

    if len( download_frame_dict ):
        #progressbar
        progress = 0
        progress_100 = len( download_frame_dict )

        update_progress_signal.emit( 'Starting download...' , progress , progress_100 )

        for doubleDashKeyString,object in download_frame_dict.iteritems():
            if os.path.exists( doubleDashKeyString ):
                print('   skipping: ' + doubleDashKeyString ) # todo MD5 check
            else:
                print('downloading: ' + doubleDashKeyString )
                #check if directory exists
                dirname=os.path.dirname(doubleDashKeyString )
                if os.path.isdir( dirname )==False:
                    os.makedirs( dirname ) # todo this has a massive overhead...refactor later
                object.get_contents_to_filename( doubleDashKeyString , cb=percent_cb , num_cb=100 )
            print( '-------------------------------' )
            progress = progress+1
            update_progress_signal.emit( os.path.basename( doubleDashKeyString ) , progress , progress_100 )
    else:
        update_progress_signal.emit( 'No images found on S3!' , 0 , 0 )

def upload_file( bucket_name , file_path , strip_path_prefix='' ):
    if os.path.isfile( file_path ):
        create_folder( bucket_name , os.path.dirname( file_path ) , recursive=True , strip_path_prefix=strip_path_prefix )
        upload_files(  bucket_name , os.path.dirname( file_path ) , [ os.path.basename( file_path ) ] , strip_path_prefix )
        return 0
    else:
        print 'Warning - file not found: ' + file_path
        return 1

def upload_files( bucket_name , source_dir , upload_file_names_list , strip_path_prefix='' , exclude_list=[] ):


    bucket = get_bucket( bucket_name )

    for exclude in exclude_list:
        if exclude in source_dir:
            print 'Directory excluded!'
            return

    dest_dir = strip_file_path (source_dir , strip_path_prefix )

    # init progress output
    counter = 0
    file_count = len( upload_file_names_list )

    for filename in upload_file_names_list:
        for exclude in exclude_list:
            if exclude in filename:
                print 'Filename excluded!'
                return

        sourcepath = os.path.join( source_dir , filename)
        dest_path   = os.path.join( dest_dir , filename)

        #check md5 of source
        try:
            sourcepath_md5 = hashlib.md5( open( sourcepath, 'rb').read()).hexdigest()
            #print sourcepath_md5
        except IOError:
            print "could not read {0}".format( filename )
            continue
        #get MD5 if file already in bucket
        #print destpath
        key = bucket.get_key( dest_path )
        if key != None:
            destpath_md5 =  key.etag[1:-1]
            if destpath_md5 == sourcepath_md5:
                #print "File is identical: {0}".format( filename )
                continue
        else:
            key = boto.s3.key.Key( bucket )
            key.key = dest_path

        print "Uploading: {0} {1} / {2}".format( filename , counter , file_count)
        #set files metadata
        key.set_metadata('uid', '1001')
        key.set_metadata('gid', '1001')
        key.set_metadata('mode', '33277') #33204=rw-rw-r--   33277=rwxrwxr-x
        # todo - implement proper duplication of mode!
        key.set_contents_from_filename(sourcepath , cb=percent_cb , num_cb=100)



def test_permissions( bucket_name , dest_path ):
    bucket = get_bucket( bucket_name )
    key = bucket.get_key( dest_path )
    #acl = key.get_acl()
    #print acl
    mode = key.get_metadata( 'mode' )
    print mode
    uid = key.get_metadata( 'uid' )
    print uid
    gid = key.get_metadata( 'gid' )
    print gid

def create_folders( bucket_name , source_dir , dir_names  , strip_source_prefix ):
    for dir_name in dir_names:
        dir_name_full = os.path.join( strip_file_path( source_dir , strip_source_prefix ) , dir_name )
        create_folder( bucket_name , dir_name_full )

def create_folder( bucket_name , folder_name , recursive=False , mode=493 , uid = 1001 , gid = 1001 , strip_path_prefix='' ):

    bucket = get_bucket( bucket_name )

    #safety first - make sure we have slash at the end of our foldername
    folder_name = strip_file_path( folder_name , strip_path_prefix ).rstrip('/') + '/'

    key = bucket.get_key( folder_name )
    if key==None:
        if recursive:
            parent_dir = os.path.dirname( folder_name.rstrip('/') )
            if parent_dir != '/':
                # print "recursing into: {0}".format(parent_dir)
                create_folder( bucket_name , parent_dir , recursive , mode , uid , gid )
        key = bucket.new_key( folder_name )
        key.set_metadata( 'mode' , mode )
        key.set_metadata( 'uid' , uid )
        key.set_metadata( 'gid' , gid )
        key.set_contents_from_string('')
        print 'Successfully created: ' + folder_name
    #else:
        #print 'Folder already exists: ' + folder_name
    return folder_name
