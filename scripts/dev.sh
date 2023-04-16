#!/usr/bin/bash
docker build . -t pop-docker:latest
docker run \
    -v ${PWD}/app:/opt/app \
    -v ${PWD}/tests:/opt/tests \
    -p 8000:8000 \
    -e PROD=0 \
    -e TOKEN=abc \
    pop-docker:latest 