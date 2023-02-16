import boto3
import constants
from datetime import datetime, timezone
import requests


class S3Client:
    def __init__(self):
        """_summary_
        """
        self.client = boto3.client('s3')
        self.ec2_client = boto3.client('ec2', region_name=constants.AWS_REGION)
        r = requests.get(constants.INSTANCE_META_DATA_URL)
        self.instance_id = r.text
        response = self.ec2_client.describe_instances(
            Filters=[{'Name': 'instance-id', 'Values': [r.text]}])
        instance = response['Reservations'][0]['Instances'][0]
        tag_name = ''
        if 'Tags' in instance:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    tag_name = tag['Value']
                    break
        self.tag_name = tag_name

    def download_file(self, bucket: str, key: str, filename: str):
        """_summary_

        Args:
            bucket (str): _description_
            key (str): _description_
            filename (str): _description_
        """
        self.client.download_file(bucket, key, filename)

    def upload_to_s3(self, image_key: str, data: str):
        """_summary_

        Args:
            image_key (_type_): _description_
            data (_type_): _description_
        """
        self.client.put_object(
            Body=data, Bucket=constants.OUTPUT_S3_BUCKET, Key=image_key)
        # self.client.put_object_tagging(
        #     Bucket=constants.OUTPUT_S3_BUCKET,
        #     Key=image_key,
        #     Tagging={
        #         'TagSet': [
        #             {
        #                 'Key': 'Image Name',
        #                 'Value': image_key
        #             },
        #             {
        #                 'Key': 'Result',
        #                 'Value': data.split(",")[-1]
        #             },
        #             {
        #                 'Key': 'Instance Name',
        #                 'Value': str(self.tag_name)
        #             },
        #             {
        #                 'Key': 'Instance ID',
        #                 'Value': str(self.instance_id)
        #             }
        #         ]
        #     }
        # )
