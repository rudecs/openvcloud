set -e
cd
cd go
go get 'git.aydo.com/0-complexity/openvcloud' || true
cd 'src/git.aydo.com/0-complexity/openvcloud/apps/oauthserver'
go get ./...
