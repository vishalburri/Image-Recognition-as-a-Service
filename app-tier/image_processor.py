import os
from image_classification import get_classified_image
from s3_client import S3Client
from sqs_client import SqsClient
from urllib.parse import urlparse


class ImageProcessor:
    def __init__(self, s3: S3Client, sqs: SqsClient):
        """_summary_

        Args:
            s3 (S3Client): _description_
            sqs (SqsClient): _description_
        """
        self.s3 = s3
        self.sqs = sqs

    def process(self, s3_object_path: str):
        """_summary_

        Args:
            s3_object_path (str): _description_
        """
        parsed_url = urlparse(s3_object_path, allow_fragments=False)
        key = parsed_url.path.lstrip('/')
        bucket = parsed_url.netloc
        self.s3.download_file(bucket, key, f'/tmp/{key}')
        result = get_classified_image(f'/tmp/{key}')
        os.remove(f'/tmp/{key}')
        img_key = key.split(".")[0]
        self.s3.upload_to_s3(img_key, result)
        self.sqs.send_message_to_queue(key, result.split(",")[-1])
        print(result)
