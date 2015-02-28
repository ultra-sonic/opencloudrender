import boto
import boto.s3
import hashlib

import os.path
import sys

# max size in bytes before uploading in parts. between 1 and 5 GB recommended
MAX_SIZE = 20 * 1000 * 1000
#size of parts when uploading in parts
PART_SIZE = 6 * 1000 * 1000

conn = boto.connect_s3()

exclude_list = ['/docs/' , '/samples/']

existing_buckets=dict()
# todo - implement proper exclude list a la rsync

def create_bucket( bucket_name ):
    # todo - debug if this is really working as expected
    if bucket_name not in existing_buckets.keys():
        try:
            bucket = conn.get_bucket(bucket_name)
        except boto.exception.S3ResponseError:
            bucket = conn.create_bucket(bucket_name,
                                        location=boto.s3.connection.Location.EU)
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
    sys.stdout.write( "sent {0} / {1}\r".format( complete , total ))
    sys.stdout.flush()

def upload_file( bucket_name , file_path , strip_path_prefix='' ):
    create_folder( bucket_name , os.path.dirname( file_path ) , recursive=True )
    upload_files(  bucket_name , os.path.dirname( file_path ) , [ os.path.basename( file_path ) ] , strip_path_prefix )

def upload_files( bucket_name , source_dir , upload_file_names_list , strip_path_prefix='' ):


    bucket = create_bucket( bucket_name )

    for exclude in exclude_list:
        if exclude in source_dir:
            print "Directory excluded!"
            return

    dest_dir = source_dir[ len( strip_path_prefix ): ]

    # init progress output
    counter = 0
    file_count = len( upload_file_names_list )

    for filename in upload_file_names_list:
        for exclude in exclude_list:
            if exclude in filename:
                print "Filename excluded!"
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
                print "File is indentical: {0}".format( filename )
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
        key.set_contents_from_filename(sourcepath , cb=percent_cb , num_cb=10)



def test_permissions( bucket_name , dest_path ):
    bucket = create_bucket( bucket_name )
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

def create_folder( bucket_name , folder_name , recursive=False , mode=493 , uid = 1001 , gid = 1001 ):

    bucket = create_bucket( bucket_name )

    #safety first - make sure we have slash at the end of our foldername
    folder_name = folder_name.rstrip('/') + '/'

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
    else:
        print 'Folder already exists: ' + folder_name
    return folder_name

def strip_file_path( file_path , strip_path_prefix  ):
    if file_path.startswith( strip_path_prefix ):
        return file_path[ len( strip_path_prefix ): ]
    else:
        return file_path









