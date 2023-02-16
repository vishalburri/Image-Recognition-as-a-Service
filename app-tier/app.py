import time
from sqs_client import SqsClient
from s3_client import S3Client
from image_processor import ImageProcessor
# import subprocess
# import constants
# import requests
# import boto3

# ec2_client = boto3.client('ec2', region_name=constants.AWS_REGION)
# r = requests.get(constants.INSTANCE_META_DATA_URL)
# response = ec2_client.describe_instances(
#     Filters=[{'Name': 'instance-id', 'Values': [r.text]}])
# instance = response['Reservations'][0]['Instances'][0]
# tag_name = ''
# isTerminated = False
# if 'Tags' in instance:
#     for tag in instance['Tags']:
#         if tag['Key'] == 'Name':
#             tag_name = tag['Value']
#             break


def process_image(sqs: SqsClient, image_processor: ImageProcessor) -> None:
    try:
        start_time = time.time()
        s3_object_path, receipt_handle = sqs.get_message_from_queue()
        print(f"s3 path : {s3_object_path}")
        if s3_object_path:
            image_processor.process(s3_object_path)
            sqs.delete_message_from_queue(receipt_handle)
        # else:
        #     subprocess.run(["sudo", "shutdown", "-h", "now"])
        #     try:
        #         _terminate_instance()
        #     except Exception as err:
        #         print(err)
    except Exception as e:
        print(e)
        # logging.info("Messages not available", e)
        time.sleep(2)


# def _terminate_instance():
#     # terminate instance if no message is found
#     global isTerminated
#     if tag_name != "app-instance-1":
#         ec2_client.terminate_instances(InstanceIds=[r.text])
#         isTerminated = True
#         return


def run_polling_job() -> None:
    # logging.basicConfig(format='%(levelname)s:%(message)s',
    # level=logging.DEBUG)
    # logging.info("Running Polling Job")
    sqs = SqsClient()
    s3_client = S3Client()
    image_processor = ImageProcessor(s3_client, sqs)

    while True:
        process_image(sqs, image_processor)
        # if isTerminated:
        #     break
        time.sleep(2)


run_polling_job()
