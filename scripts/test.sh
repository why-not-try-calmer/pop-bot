#!/usr/bin/bash
docker run \
    -v $(pwd)/app:/opt/app \
    -v $(pwd)/tests:/opt/tests \
    -p 8000:8000 \
    --env-file=$(pwd)/.env \
    pop-ready:latest bash -c "cd /opt && python3 -m pytest tests/tests.py -v -s" 