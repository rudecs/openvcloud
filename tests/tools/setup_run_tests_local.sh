#!/bin/bash

branch=$1
directory=$2 #any dir on the master node to clone the test repo Ex.: /opt/code/
environment=$3
testsuite=$4

GREEN='\033[0;32m' # Green color
NC='\033[0m'       # No color
echo -e "${GREEN}*** Start script setup_run_tests_local ...${NC}"

mkdir -p $directory
cd $directory
rm -rf G8_testing
ssh-add -l
#chmod g-r /root/.ssh/id_awesomo
echo -e "${GREEN}** Clone G8_testing $branch branch ...${NC}"
ssh-add -l
git clone -b $branch git@github.com:0-complexity/G8_testing.git
cd G8_testing
echo -e "${GREEN}** Update the config.ini with the environment correct value $environment...${NC}"
sed -i "2s/.*/environment = $environment/" functional_testing/Openvcloud/config.ini
echo -e "${GREEN}** Activating JumpScale virtual env ...${NC}"
source /opt/jumpscale7/env.sh
echo -e "${GREEN}** Checking python-pip ...${NC}";
which pip || apt-get install -y python-pip
echo -e "${GREEN}** Installing G8_testing requirements ...${NC}"
pip install -r requirements.txt
cd functional_testing/Openvcloud/
echo -e "${GREEN}** Running tests ...${NC}"
nosetests $testsuite --with-xunit --xunit-file='testresults.xml' --with-progressive --tc-file=config.ini
echo -e "${GREEN}*** End script setup_run_tests_local ...${NC}"
