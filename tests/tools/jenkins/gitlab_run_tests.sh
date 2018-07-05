#!/bin/bash

environment=$1
node=$2
sourcebranch=$3
targetbranch=$4

eval $(bash tools/gen_connection_params.sh $environment $node) # This script returns SSHKEY, PROXY and HOST
script="'bash -s' < tools/jenkins/gitlab_run_tests_local.sh $sourcebranch $targetbranch"

eval "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -M -l root -i $SSHKEY -o ProxyCommand=\"$PROXY\" $HOST $script"

# Collect result
rm -rf logs/
mkdir logs/
eval "scp -r -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i $SSHKEY -o ProxyCommand=\"$PROXY\" root@$HOST:/opt/code/OpenVCloud_testsuite/logs/* logs/"

# Copy test results
eval "scp -r -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i $SSHKEY -o ProxyCommand=\"$PROXY\" root@$HOST:/opt/code/OpenVCloud_testsuite/testresults.xml ."