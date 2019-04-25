import boto3
import os
from datetime import datetime
import argparse

# http://notes.webutvikling.org/boto3-copying-and-creating-files-cloudfront-invalidations/


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()

    aws_profile = os.environ['DECRYPT_TOKYO_AWS_PROFILE']
    bucket_name = os.environ['DECRYPT_TOKYO_S3_BUCKET']
    cloudfront_dist_id = os.environ['DECRYPT_TOKYO_CLOUDFRONT_DIST_ID']

    # ####
    # # 1. SYNC S3
    # ####
    all_files = ['index.html', 'index-eng.html', 'js/*', 'css/*', 'images/*', 'upload/*']
    include_string = ' '.join('--include "%s"' % file for file in all_files)

    aws_command = 'aws s3 sync . s3://%s --profile %s --exclude "*" %s' % (
        bucket_name, aws_profile, include_string
    )
    os.system(aws_command)

    ####
    # 2. Invalidate Cloudfront Cache
    ####
    boto3.setup_default_session(profile_name=aws_profile)

    files = (
        all_files
        if args.force
        else ['index.html', 'index-eng.html']
    )
    cloudfront = boto3.client('cloudfront')
    cloudfront.create_invalidation(
        DistributionId=cloudfront_dist_id,
        InvalidationBatch={
            'Paths': {
                'Quantity': len(files),
                'Items': ['/{}'.format(f) for f in files]
            },
            'CallerReference': 'my-references-{}'.format(datetime.now())
        }
    )
