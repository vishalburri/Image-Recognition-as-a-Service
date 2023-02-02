from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.templating import Jinja2Templates
from s3_client import S3Client

app = FastAPI()

# Load the Jinja2 template
templates = Jinja2Templates(directory="templates")
INPUT_S3_BUCKET = 'cse546-project1-input-s3'
s3_client = S3Client()


@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/")
def upload_files(files: list[UploadFile] | None):
    for file in files:
        if file.filename != '':
            s3_client.upload_file_to_s3(file, INPUT_S3_BUCKET)
    raise HTTPException(status_code=302, headers={"Location": "/"})
