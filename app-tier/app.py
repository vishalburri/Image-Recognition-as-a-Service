import os
import boto3
from s3_url import S3Url
from image_classification import get_classified_image
import time
from datetime import datetime, timezone
import subprocess
import requests
import json
# Define AWS Region
aws_region = 'us-east-1'
# SQS Queue URL
queue_url = 'https://sqs.us-east-1.amazonaws.com/376277702783/CSE-546-project1-request-queue'


# Instantiate Clients
sqs = boto3.client('sqs', region_name=aws_region)
s3 = boto3.client('s3')
ec2 = boto3.client('ec2', region_name=aws_region)
# Obtain Instance ID of instance
r = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
instance_id = r.text


def get_num_messages_available():
    """ Returns the number of messages in the queue """
    response = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=[
                                        'ApproximateNumberOfMessages'])
    messages_available = response['Attributes']['ApproximateNumberOfMessages']
    return int(messages_available)


def get_latest_message():
    """ Gets the first available message in queue """
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        MessageAttributeNames=['All'],
        VisibilityTimeout=10,
        WaitTimeSeconds=0
    )
    receipt_handle = response['Messages'][0]['ReceiptHandle']
    s3_object_path = json.loads(response['Messages'][0]['Body'])
    bucket = s3_object_path['Records'][0]['s3']['bucket']['name']
    key = s3_object_path['Records'][0]['s3']['object']['key']
    s3_object_path = "s3://{}/{}".format(bucket, key)
    return s3_object_path, receipt_handle


def delete_message(receipt_handle):
    """ Deletes the SQS message that matches the specified handle """
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )


def process_image(s3_object_path):
    s = S3Url(s3_object_path)
    s3.download_file(s.bucket, s.key, f'/tmp/{s.key}')
    result = get_classified_image(f'/tmp/{s.key}')
    os.remove(f'/tmp/{s.key}')

    print(result)


def run_job():
    while get_num_messages_available() > 0:
        try:
            print("Retrieving Image Link from SQS")
            s3_object_path, receipt_handle = get_latest_message()
            process_image(s3_object_path)
            delete_message(receipt_handle)
            print("Successfully Processed {}".format(s3_object_path))
            # time.sleep(1)
        except:
            print("No more messages available")
            time.sleep(2)


while True:
    print("Running Job")
    run_job()
    time.sleep(5)  # poll every 5 seconds
