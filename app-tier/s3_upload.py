import boto3
from datetime import datetime, timezone
import requests

bucket_name = 'cse546-project1-output-s3'
client = boto3.client('s3')
r = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
instance_id = r.text


def upload_to_s3(image_key, data):
    client.put_object(Body=data, Bucket=bucket_name, Key=image_key)
    put_tags_response = client.put_object_tagging(
        Bucket=bucket_name,
        Key=image_key,
        Tagging={
            'TagSet': [
                {
                    'Key': 'Image',
                    'Value': image_key
                },
                {
                    'Key': 'Output',
                    'Value': data.split(",")[-1]
                },
                {
                    'Key': 'Instance',
                    'Value': str(instance_id)
                },
                {
                    'Key': 'ExecutedOn',
                    'Value': str(datetime.now(timezone.utc))
                }
            ]
        }
    )
