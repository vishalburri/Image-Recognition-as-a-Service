import time
from sqs_client import SqsClient
from s3_client import S3Client
from image_processor import ImageProcessor
# import logging


def process_image(sqs: SqsClient, image_processor: ImageProcessor) -> None:
    try:
        # logging.info("Received Image link from SQS")
        start_time = time.time()
        s3_object_path, receipt_handle = sqs.get_message_from_queue()
        print(f"s3 path : {s3_object_path}")
        if s3_object_path:
            image_processor.process(s3_object_path)
            # time.sleep(0.5)
            sqs.delete_message_from_queue(receipt_handle)
        total_time = time.time() - start_time
        # logging.info(
        # f"Successfully Processed {s3_object_path} in {total_time} seconds")
    except Exception as e:
        print(e)
        # logging.info("Messages not available", e)
        time.sleep(2)


def run_polling_job() -> None:
    # logging.basicConfig(format='%(levelname)s:%(message)s',
    # level=logging.DEBUG)
    # logging.info("Running Polling Job")
    sqs = SqsClient()
    s3_client = S3Client()
    image_processor = ImageProcessor(s3_client, sqs)

    while True:
        process_image(sqs, image_processor)


run_polling_job()
