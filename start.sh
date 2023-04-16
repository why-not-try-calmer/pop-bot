#!/usr/bin/bash
case "$1" in
    "test" ) PROD=0 python3 -m pytest -s -v ;;
    * ) python3 -m app ;;
esac