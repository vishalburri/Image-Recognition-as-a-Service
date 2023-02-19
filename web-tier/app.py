from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.templating import Jinja2Templates
from s3_client import S3Client
from sqs_client import SqsClient
from threading import Thread, Lock
import time
import json
import asyncio
from ec2_scalar import auto_scale
app = FastAPI()

# Load the Jinja2 template
templates = Jinja2Templates(directory="templates")
INPUT_S3_BUCKET = 'cse546-project1-input-s3'
s3_client = S3Client()
sqs_client = SqsClient()
result_dict = {}
lock = Lock()


async def get_result(key):
    """_summary_

    Args:
        key (_type_): _description_

    Returns:
        _type_: _description_
    """
    while True:
        await asyncio.sleep(1)
        with lock:
            if key in result_dict:
                output_to_be_returned = '{0}'.format(result_dict[key])
                del result_dict[key]
                return output_to_be_returned


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/")
async def upload_files(files: list[UploadFile] | None):
    for file in files:
        if file.filename != '':
            s3_client.upload_to_s3(file, INPUT_S3_BUCKET)
            result = await get_result(file.filename)
            print(result)
    raise HTTPException(status_code=302, headers={"Location": "/"})


@app.post("/upload")
async def upload(file: UploadFile):
    """_summary_

    Args:
        file (UploadFile): _description_

    Returns:
        _type_: _description_
    """
    try:
        s3_client.upload_to_s3(file, INPUT_S3_BUCKET)
        result = await get_result(file.filename)
        return result
    except Exception as e:
        print(e)


def get_response():
    while True:
        messages = sqs_client.get_messages_from_queue()
        for message in messages:
            receipt_handle = message['ReceiptHandle']
            message_body = message['Body']
            message_dict = json.loads(message_body)
            result_dict[message_dict['Key']] = message_dict['Value']
            sqs_client.delete_message_from_queue(receipt_handle)
        time.sleep(1)


response_thread = Thread(target=get_response)
# response_thread1 = Thread(target=auto_scale)

response_thread.start()
# response_thread1.start()
