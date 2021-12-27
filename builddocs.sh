#!/usr/bin/env bash

# shellcheck disable=SC1091
source venv/bin/activate

cd docs || exit
make clean html
cd ..
