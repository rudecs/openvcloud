#!/bin/bash

apt update
apt-get install python-dev build-essential libssl-dev libffi-dev \
libxml2-dev libxslt1-dev zlib1g-dev \
python-pip python3-pip iputils-ping tmux wget unzip xvfb chromium-chromedriver -y

# install requirements
pip install -r requirements.txt
pip3 install -r ovc_master_hosted/Portal/requirements.txt

# change portal folder premissions
chmod 777 ovc_master_hosted/Portal

# link chromedriver
ln -fs /usr/lib/chromium-browser/chromedriver /usr/bin/chromedriver
ln -fs /usr/lib/chromium-browser/chromedriver /usr/local/bin/chromedriver