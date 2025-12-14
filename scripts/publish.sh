#!/usr/bin/env bash

python -m twine upload dist/* -u __token__ -p "$PYPI_TOKEN"
