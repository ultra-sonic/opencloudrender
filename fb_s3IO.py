import boto
import boto.s3

import os.path
import sys

# Fill in info on data to upload
# destination bucket name
bucket_name = 'fbcloudrender-testdata'
# source directory
sourceDir = 'testData/'
# destination directory name (on s3)
destDir = ''

# max size in bytes before uploading in parts. between 1 and 5 GB recommended
MAX_SIZE = 20 * 1000 * 1000
#size of parts when uploading in parts
PART_SIZE = 6 * 1000 * 1000

conn = boto.connect_s3()

try:
    bucket = conn.get_bucket(bucket_name)
except boto.exception.S3ResponseError:
    bucket = conn.create_bucket(bucket_name,
                                location=boto.s3.connection.Location.EU)


def get_files_in_directory(sourceDir):
    uploadFileNames = []
    for (sourceDir, dirname, filename) in os.walk(sourceDir):
        uploadFileNames.extend(filename)
        break
    return uploadFileNames


def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()


def upload_files( bucketname , uploadFileNames , root_folder="" ):
    for filename in uploadFileNames:
        sourcepath = os.path.join(sourceDir + filename)
        destpath = os.path.join(destDir, filename)
        print 'Uploading %s to Amazon S3 bucket %s' % \
              (sourcepath, bucket_name)

        filesize = os.path.getsize(sourcepath)
        if filesize > MAX_SIZE:
            print "multipart upload"
            mp = bucket.initiate_multipart_upload(destpath)
            fp = open(sourcepath, 'rb')
            fp_num = 0
            while (fp.tell() < filesize):
                fp_num += 1
                print "uploading part %i" % fp_num
                mp.upload_part_from_file(fp, fp_num, cb=percent_cb, num_cb=10, size=PART_SIZE)

            mp.complete_upload()

        else:
            print "singlepart upload"
            k = boto.s3.key.Key(bucket)
            k.key = destpath
            k.set_contents_from_filename(sourcepath,
                                         cb=percent_cb, num_cb=10)