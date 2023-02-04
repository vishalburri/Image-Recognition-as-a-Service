#!/bin/bash

sudo -u ubuntu sh -c "cd /home/ubuntu/Image-Recognition-as-a-Service/web-tier && git pull && uvicorn app:app --port 8080 --host 0.0.0.0"