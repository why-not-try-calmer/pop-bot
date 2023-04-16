#!/usr/bin/bash
docker run \
    -v ${PWD}/app:/opt/app \
    -v ${PWD}/tests:/opt/tests \
    -p 8000:8000 \
    -e PROD=0 \
    pop-docker:latest bash -c "cd /opt && python3 -m pytest -v -s" 