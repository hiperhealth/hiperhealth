#!/usr/bin/env bash

python -m build
python -m twine check dist/*
