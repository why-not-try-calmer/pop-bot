#!/usr/bin/bash
docker run \
    -v $(pwd)/app:/opt/app \
    -p 8000:8000 \
    --env-file=$(pwd)/.env \
    pop-ready:latest