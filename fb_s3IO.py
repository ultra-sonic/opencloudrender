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

def get_files_in_directory(sourceDir , recursive=False ):
    uploadFileNames = []
    for (sourceDir, dirname, filename) in os.walk( sourceDir ):
        uploadFileNames.extend(filename)
    return uploadFileNames


def percent_cb(complete, total):
    sys.stdout.write( "sent {0} / {1}\r".format( complete , total ))
    sys.stdout.flush()


def upload_files( bucket_name , sourceDir , uploadFileNames , sourcePrefix ):
    try:
        bucket = conn.get_bucket(bucket_name)
    except boto.exception.S3ResponseError:
        bucket = conn.create_bucket(bucket_name,
                                    location=boto.s3.connection.Location.EU)

    destDir = sourceDir[ len( sourcePrefix ): ]
    for filename in uploadFileNames:
        sourcepath = os.path.join( sourceDir , filename)
        destpath   = os.path.join( destDir , filename)

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

        print "Uploading: {0}".format( filename )
        #metadata test
        key.set_metadata('uid', '1088')
        key.set_metadata('gid', '1000')
        key.set_metadata('mode', '33277') #33204=rw-rw-r--   33277=rwxrwxr-x
        key.set_contents_from_filename(sourcepath , cb=percent_cb , num_cb=10)
