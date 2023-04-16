#!/usr/bin/bash
docker build . -t pop-docker:latest
docker run -it pop-docker:latest bash