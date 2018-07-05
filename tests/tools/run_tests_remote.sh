#!/bin/bash

GREEN='\033[0;32m' # Green color
NC='\033[0m'       # No color

usage(){
	echo "This script to run Openvcloud test suite on remote grid"
	echo -e "\nUsage:\n$0 [options] [grid] \n"
	echo "Options:"
	echo "    -n    node on the grid"
	echo "    -b    testsuite branch to run tests from"
	echo "    -d    directory to install the testsuite"
	echo "    -c    controller node port"
}

if [[ ( $1 == "--help") ||  $1 == "-h" ]]
then
	usage
	exit 0
fi

OPTIND=1
while getopts ":n:b:d:c:" opt; do
  case $opt in
    n) node="$OPTARG";;
    b) branch="$OPTARG";;
    d) directory="$OPTARG";;
		c) ctrlport="$OPTARG";;
    \?) echo "Invalid option -$OPTARG" >&2 ; exit 1;;
  esac
done
shift $((OPTIND-1))
if [[ -z $1 ]]
then
    usage
    exit 1
fi
grid=$1
environment=$2
testsuite=$3
node=${node:-ovc_master}
branch=${branch:-master}
ctrlport=${ctrlport:-22}
dir=`uuidgen`
directory=${directory:-/opt/code/$dir}
echo -e "${GREEN}** Session working directory is: [$directory]${NC}"

jenkins_key="$HOME/.ssh/id_awesomo"
private_key="$HOME/.ssh/id_rsa"
if [ -e $jenkins_key ]; then
	echo $jenkins_key
	eval $(ssh-agent -s)
	ssh-add $jenkins_key
elif [ -e $private_key ]; then
	echo $private_key
	eval $(ssh-agent -s)
	ssh-add $private_key
else
	echo -e "${GREEN}** no private key found ${NC}"
fi
ssh-add -l

eval $(bash tools/gen_connection_params.sh $grid $node $ctrlport) # This script returns SSHKEY, PROXY and HOST

script="'bash -s' < tools/setup_run_tests_local.sh $branch $directory $environment $testsuite "
eval "ssh -A -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -M -l root -i $SSHKEY -o ProxyCommand=\"$PROXY\" $HOST $script"

echo -e "${GREEN}** Collect logs and result..${NC}"
# Collect result
rm -rf logs/
mkdir logs/
eval "scp -r -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i $SSHKEY -o ProxyCommand=\"$PROXY\" root@$HOST:$directory/G8_testing/functional_testing/Openvcloud/logs/* logs/" 2> /dev/null

# Copy test results
eval "scp -r -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i $SSHKEY -o ProxyCommand=\"$PROXY\" root@$HOST:$directory/G8_testing/functional_testing/Openvcloud/testresults.xml ." 2> /dev/null

#delete test suite directory from the environment node
script="rm -rf $directory"
eval "ssh -A -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -M -l root -i $SSHKEY -o ProxyCommand=\"$PROXY\" $HOST $script" 2> /dev/null
echo -e "${GREEN}** DONE **${NC}"
