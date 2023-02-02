import boto3
import json

# Define AWS Region
aws_region = 'us-east-1'
# SQS Queue URL
queue_url = 'https://sqs.us-east-1.amazonaws.com/376277702783/CSE-546-project1-response-queue'
sqs = boto3.client('sqs', region_name=aws_region)


def send_message_to_sqs(image_key, image_value):
    response = sqs.send_message(QueueUrl=queue_url,
                                MessageBody=json.dumps({'Key': image_key, 'Value': image_value}))
