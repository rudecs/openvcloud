#!/bin/sh

set -e
cd

. ~/.bashrc

sh setup_oauth.sh
cd go/src/git.aydo.com/0-complexity/openvcloud/apps/oauthserver
go run main.go
