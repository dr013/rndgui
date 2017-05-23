#!/usr/bin/env bash

if [ -d venv ]; then
    rm -rf venv
fi;

/usr/local/bin/virtualenv --no-site-packages venv
source venv/bin/activate
pip install -q 'requests[security]'
pip install -q -U pip setuptools
pip install -q -r requirements/test.txt --upgrade
