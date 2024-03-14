import boto3

s3 = boto3.resource('s3')
bucket = s3.Bucket('aws-wafr-automation-reports')
bucket.object_versions.all().delete()