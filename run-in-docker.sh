#!/bin/bash

docker build -t pvoutput . || exit 1

docker run --rm -it \
    -v "$(pwd)/pvoutput.json:/home/useruser/pvoutput/pvoutput.json" \
    --name pvoutput \
    pvoutput \
    bash
