#!/bin/bash

set -xe

virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
cd auto_generated_docs/
make clean
make html
