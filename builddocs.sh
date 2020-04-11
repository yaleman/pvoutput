#!/usr/bin/env bash

cd docs || exit
pipenv run make clean html
cd ..
