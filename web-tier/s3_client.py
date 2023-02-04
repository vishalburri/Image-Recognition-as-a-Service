import boto3
from fastapi import UploadFile


class S3Client:
    def __init__(self):
        """_summary_
        """
        self.client = boto3.client('s3')

    def upload_to_s3(self, file: UploadFile, bucket_name: str):
        """
        Uploads the given input file to s3 bucket

        Args:
            file (UploadFile): _description_
            bucket_name (str): _description_
        """
        self.client.upload_fileobj(
            file.file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )
