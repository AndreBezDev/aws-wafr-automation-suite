import boto3

#define bucket to be recursively cleared
bucket = 'aws-wafr-automation-reports'

def s3_clear_recursive(bucket):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
    bucket.object_versions.all().delete()