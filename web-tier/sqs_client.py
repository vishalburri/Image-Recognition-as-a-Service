import boto3

AWS_REGION = 'us-east-1'
SQS_RESPONSE_URL = 'https://sqs.us-east-1.amazonaws.com/376277702783/CSE-546-project1-response-queue'


class SqsClient:
    def __init__(self, region_name: str = AWS_REGION):
        """_summary_

        Args:
            region_name (str, optional): _description_. Defaults to constants.AWS_REGION.
        """
        self.client = boto3.client('sqs', region_name=region_name)

    def get_messages_from_queue(self):
        """
        Gets the latest available messages in the queue

        Returns:
            list of messages
        """
        response = self.client.receive_message(
            QueueUrl=SQS_RESPONSE_URL,
            MaxNumberOfMessages=10,
            VisibilityTimeout=10,
            WaitTimeSeconds=10
        )
        return response.get('Messages', [])

    def delete_message_from_queue(self, receipt_handle: str):
        """
        Deletes the SQS message with given receipt_handle

        Args:
            receipt_handle (str): _description_
        """
        self.client.delete_message(
            QueueUrl=SQS_RESPONSE_URL,
            ReceiptHandle=receipt_handle
        )
