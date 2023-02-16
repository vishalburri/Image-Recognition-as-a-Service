import boto3
import json
import constants
# import requests


class SqsClient:
    def __init__(self, region_name: str = constants.AWS_REGION):
        """_summary_

        Args:
            region_name (str, optional): _description_. Defaults to constants.AWS_REGION.
        """
        self.client = boto3.client('sqs', region_name=region_name)

    def get_approximate_messages_from_queue(self) -> int:
        """
        Gets the approximate number of messages in the queue from queue attributes

        Returns:
            int: number of messages in queue
        """
        response = self.client.get_queue_attributes(QueueUrl=constants.SQS_REQUEST_URL, AttributeNames=[
            'ApproximateNumberOfMessages'])
        num_of_messages = response['Attributes']['ApproximateNumberOfMessages']
        return int(num_of_messages)

    def get_message_from_queue(self) -> tuple[str, str]:
        """
        Gets the latest available message in the queue

        Returns:
            Tuple[str, str]: returns s3_object_path and receipt_handle of the message
        """
        try:
            response = self.client.receive_message(
                QueueUrl=constants.SQS_REQUEST_URL,
                MaxNumberOfMessages=1,
                VisibilityTimeout=20,
                MessageAttributeNames=['All'],
                WaitTimeSeconds=20
            )
            # if 'Messages' not in response or len(response['Messages']) == 0:
            #     # terminate this instance
            #     instance_id = requests.get(
            #         'http://169.254.169.254/latest/meta-data/instance-id').text
            #     ec2 = boto3.client('ec2')
            #     ec2.terminate_instances(InstanceIds=[instance_id])
            #     return (None, None)
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']
            s3_path_dict = json.loads(message['Body'])
            bucket_name = s3_path_dict['Records'][0]['s3']['bucket']['name']
            key_name = s3_path_dict['Records'][0]['s3']['object']['key']
            s3_path = f"s3://{bucket_name}/{key_name}"

            return s3_path, receipt_handle
        except Exception as e:
            print("Exception", e)
            return (None, None)

    def delete_message_from_queue(self, receipt_handle: str):
        """
        Deletes the SQS message with given receipt_handle

        Args:
            receipt_handle (str): _description_
        """
        try:
            self.client.delete_message(
                QueueUrl=constants.SQS_REQUEST_URL,
                ReceiptHandle=receipt_handle
            )
        except Exception as e:
            print(e)

    def send_message_to_queue(self, image_key: str, image_value: str):
        """
        Sends a message to queue in the form of Key Value Pair

        Args:
            image_key (_type_): _description_
            image_value (_type_): _description_
        """
        try:
            response = self.client.send_message(
                QueueUrl=constants.SQS_RESPONSE_URL,
                MessageBody=json.dumps(
                    {'Key': image_key, 'Value': image_value}),
            )
        except Exception as e:
            print(e)
