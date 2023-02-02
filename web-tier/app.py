from fastapi import FastAPI, UploadFile, HTTPException, Request
import boto3
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Load the Jinja2 template
templates = Jinja2Templates(directory="templates")


def upload_file_to_s3(file: UploadFile, bucket_name):
    s3 = boto3.client("s3")
    try:
        s3.upload_fileobj(
            file.file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        print("Something Happened: ", e)
        return e


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/")
def upload_files(files: list[UploadFile] | None):
    for uploaded_file in files:
        print(uploaded_file.filename)
        if uploaded_file.filename != '':
            upload_file_to_s3(uploaded_file, 'cse546-project1-input-s3')
    raise HTTPException(status_code=302, headers={"Location": "/"})
