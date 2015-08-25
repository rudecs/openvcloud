## OAuth2 server


## Configuration using toml

 1. Create a new user in users.toml
 2. Generate a password and edit users.toml

```sh
cd $GOPATH/0-complexity/openvcloud/apps/oauthserver/users/main
go run generate.go 'yourpassword'
```

## Test using curl

```
curl "http://localhost:8080/login/oauth/authorize?response_type=code&client_id=dcpm&redirect_uri=http%3A%2F%2Flocalhost%3A1543%2Fauthcallback&scope=dcpm" -v

curl "http://localhost:8080/login/oauth/authorize?response_type=code&client_id=dcpm&redirect_uri=http%3A%2F%2Flocalhost%315430%2Fauthcallback&scope=dcpm" -v -d login=your_user -d password=your_pwd

curl "http://localhost:8080/login/oauth/access_token" -v  -d grant_type=authorization_code -d client_id=dcpm -d client_secret=WhateverSecretYouWant -d redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauthcallback -d code=<frompreviousresponse>

```
