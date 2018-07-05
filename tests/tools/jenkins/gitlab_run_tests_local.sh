#!/bin/bash

sourcebranch=$1
targetbranch=$2
GREEN='\033[0;32m' # Green color
NC='\033[0m'       # No color

mkdir -p /opt/code
cd /opt/code
rm -rf OpenVCloud_testsuite
echo -e "${GREEN}** Clone OpenVCloud_testsuite $targetbranch branch ...${NC}"
git clone -b $targetbranch https://jenkins:alorotom007@git.aydo.com/quality/OpenVCloud_testsuite.git
cd OpenVCloud_testsuite
echo -e "${GREEN}** Merge $sourcebranch into $targetbranch ...${NC}"
git merge --no-commit origin/$sourcebranch
echo -e "${GREEN}** Activating JumpScale virtual env ...${NC}"
source /opt/jumpscale7/env.sh
echo -e "${GREEN}** Checking python-pip ...${NC}";
which pip || apt-get install -y python-pip
echo -e "${GREEN}** Installing OpenVCloud_testsuite requirements ...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}** Running tests ...${NC}"
nosetests --with-xunit --xunit-file='testresults.xml' --with-progressive