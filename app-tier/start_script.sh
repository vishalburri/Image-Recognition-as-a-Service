#!/bin/bash

sudo -u ubuntu sh -c "cd /home/ubuntu/Image-Recognition-as-a-Service/app-tier  \ 
&& git pull && cp ../../imagenet-labels.json . \ 
 && python3 app.py"