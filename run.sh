#!/usr/bin/bash
docker run \
    -v $(pwd)/app:/opt/app:ro nycticoracs/pop_os:22.04 \
    bash -c "cd /opt && python3 -m app"