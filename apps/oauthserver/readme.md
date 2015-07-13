## OAuth2 server



## Test using curl

```
curl "http://localhost:8080/login/oauth/authorize?response_type=code&client_id=dcpm&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauthcallback&scope=dcpm_admin" -v

curl "http://localhost:8080/login/oauth/authorize?response_type=code&client_id=dcpm&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauthcallback&scope=dcpm_admin" -v -d login=rob -d password=MySuperSecretPassword

curl "http://localhost:8080/login/oauth/access_token" -v  -d grant_type=authorization_code -d client_id=dcpm -d client_secret=WhateverSecretYouWant -d redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauthcallback -d code=<frompreviousresponse>

```
