#!/usr/bin/bash
docker run \
    -v $(pwd)/app:/opt/app \
    -p 8000:8000 \
    --env-file=$(pwd)/.env \
    pop-ready:latest bash -c "cd /opt && python3 -m app"
# nycticoracs/pop_os:22.04 bash -c "cd /opt && python3 -m app"