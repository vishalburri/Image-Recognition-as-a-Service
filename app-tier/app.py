import time
from sqs_client import SqsClient
from image_processor import ImageProcessor


def process_image(sqs: SqsClient, image_processor: ImageProcessor) -> None:
    while sqs.get_approximate_messages_from_queue() > 0:
        try:
            print("Retrieving Image Link from SQS")
            s3_object_path, receipt_handle = sqs.get_message_from_queue()
            image_processor.process_image(s3_object_path)
            sqs.delete_message_from_queue(receipt_handle)
            print("Successfully Processed {}".format(s3_object_path))
        except:
            print("No more messages available")
            time.sleep(2)


def run_polling_job() -> None:
    sqs = SqsClient()
    image_processor = ImageProcessor(sqs)

    while True:
        print("Running Job")
        process_image(sqs, image_processor)
        time.sleep(5)  # poll every 5 seconds


run_polling_job()
