#!/usr/bin/env bash

rm dist/*
pipenv run python setup.py sdist bdist_wheel

./builddocs.sh
