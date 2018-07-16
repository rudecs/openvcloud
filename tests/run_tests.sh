#!/bin/bash
set -o pipefail

TESTSUITE=${1}
TESTS_PATH=${2}
LOGFILE="/tmp/${TESTSUITE}.log"

if [[ ${TESTSUITE} == "acl" ]] || [[ ${TESTSUITE} == "ovc" ]]; then

    export PYTHONPATH=/opt/jumpscale7/lib:/opt/jumpscale7/lib/lib-dynload/:/opt/jumpscale7/bin:/opt/jumpscale7/lib/python.zip:/opt/jumpscale7/lib/plat-x86_64-linux-gnu
    nosetests-2.7 -s -v ${TESTS_PATH} --tc-file config.ini 2>&1 | tee ${LOGFILE}

elif [[ ${TESTSUITE} == "portal" ]]; then

    export PYTHONPATH=./
    cd ovc_master_hosted/Portal
    su - test -c "xvfb-run -a nosetests -s -v ${TESTS_PATH} --tc-file config.ini 2>&1 | tee ${LOGFILE}" 

else
    echo "Invalid testsuite name"
fi 