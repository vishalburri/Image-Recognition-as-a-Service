#!/bin/bash

su ubuntu && cd /home/ubuntu/Image-Recognition-as-a-Service/app-tier && \
	cp ../../imagenet-labels.json . && git pull && \
	python3 app.py