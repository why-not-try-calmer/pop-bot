#!/usr/bin/bash
docker build . -t pop-docker:latest
docker run \
    -v ${PWD}/app:/opt/app \
    -v ${PWD}/tests:/opt/tests \
    -e PROD=0 \
    pop-docker:latest bash -c "cd /opt && python3 -m pytest -o log_cli=true -o log_file_level=DEBUG"
