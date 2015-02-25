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
    try:
        bucket = conn.get_bucket(bucket_name)
    except boto.exception.S3ResponseError:
        bucket = conn.create_bucket(bucket_name,
                                    location=boto.s3.connection.Location.EU)
    existing_buckets[ bucket_name ] = bucket


def get_files_in_directory(source_dir , recursive=False ):
    uploadFileNames = []
    for (source_dir, dirname, filename) in os.walk( source_dir ):
        uploadFileNames.extend(filename)
    return uploadFileNames


def percent_cb(complete, total):
    sys.stdout.write( "sent {0} / {1}\r".format( complete , total ))
    sys.stdout.flush()

def upload_file( bucket_name , file_name ):
    upload_files( bucket_name , os.path.dirname( file_name ) , [ os.path.basename( file_name ) ] )

def upload_files( bucket_name , source_dir , upload_file_names_list , strip_source_prefix='' ):

    if bucket_name not in existing_buckets.keys():
        create_bucket( bucket_name )
    bucket = existing_buckets[ bucket_name ]

    for exclude in exclude_list:
        if exclude in source_dir:
            print "Directory excluded!"
            return

    dest_dir = source_dir[ len( strip_source_prefix ): ]
    # todo set folder metadata
    """try:
        folder = 'testfolder/'
        key = bucket.get_key( folder )
        key.set_contents_from_string( '' )
        #key.set_metadata('uid', '1001')
        #key.set_metadata('gid', '1001')
        #key.set_metadata('mode', '33204') #33204=rw-rw-r--   33277=rwxrwxr-x
        # todo - implement proper duplication of mode!
    except:
        print "Setting metadata failed on directory: {0}".format( folder )
    """
    # init progress output
    counter = 0
    file_count = len( upload_file_names_list )

    for filename in upload_file_names_list:
        for exclude in exclude_list:
            if exclude in filename:
                print "Filename excluded!"
                return

        sourcepath = os.path.join( source_dir , filename)
        destpath   = os.path.join( dest_dir , filename)

        #check md5 of source
        try:
            sourcepath_md5 = hashlib.md5( open( sourcepath, 'rb').read()).hexdigest()
            #print sourcepath_md5
        except IOError:
            print "could not read {0}".format( filename )
            continue
        #get MD5 if file already in bucket
        #print destpath
        key = bucket.get_key( destpath )
        if key != None:
            destpath_md5 =  key.etag[1:-1]
            if destpath_md5 == sourcepath_md5:
                print "File is indentical: {0}".format( filename )
                continue
        else:
            key = boto.s3.key.Key( bucket )
            key.key = destpath

        print "Uploading: {0} {1} / {2}".format( filename , counter , file_count)
        #set files metadata
        key.set_metadata('uid', '1001')
        key.set_metadata('gid', '1001')
        key.set_metadata('mode', '33277') #33204=rw-rw-r--   33277=rwxrwxr-x
        # todo - implement proper duplication of mode!
        key.set_contents_from_filename(sourcepath , cb=percent_cb , num_cb=10)




















