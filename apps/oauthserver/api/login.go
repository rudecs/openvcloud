package api

import (
	"fmt"
	"log"
	"net/http"
	"net/url"
	"strings"

	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/util"

	"github.com/RangelReale/osin"
	"github.com/gin-gonic/gin"
)

func (api *API) validateLogin(c *gin.Context) {
	var r struct {
		Login        string `json:"login" binding:"required"`
		Password     string `json:"password" binding:"required"`
		SecurityCode string `json:"securityCode"`
	}

	if err := c.BindJSON(&r); err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
		return
	}

	_, status := api.UserStore.Validate(r.Login, r.Password, r.SecurityCode)

	if status == nil {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	} else if status == users.InvalidPasswordError || status == users.UserNotFoundError {
		c.JSON(http.StatusOK, gin.H{"status": "invalid_password"})
	} else if status == users.InvalidSecurityCodeError {
		c.JSON(http.StatusOK, gin.H{"status": "invalid_security_code"})
	} else {
		c.AbortWithError(http.StatusInternalServerError, status)
	}
}

func (api *API) validateOauth(c *gin.Context) {
	resp := api.OsinServer.NewResponse()
	defer resp.Close()

	c.Request.ParseForm()
	log.Println("Form", c.Request.Form)

	if ar := api.OsinServer.HandleAuthorizeRequest(resp, c.Request); ar != nil {
		if !api.validateOauthRequest(c, ar) {
			return
		}
		ar.Authorized = true
		api.OsinServer.FinishAuthorizeRequest(resp, c.Request, ar)
	}
	if resp.IsError && resp.InternalError != nil {
		fmt.Printf("ERROR: %s\n", resp.InternalError)
		c.AbortWithError(http.StatusInternalServerError, resp.InternalError)
		return
	}

	log.Println("Response:", resp)
	if resp.Type == osin.REDIRECT {
		v := url.Values{}
		if s := resp.Output["code"].(string); s != "" {
			v.Set("code", s)
		}
		if s := resp.Output["state"].(string); s != "" {
			v.Set("state", s)
		}
		c.JSON(http.StatusOK, gin.H{
			"action": "redirect",
			"url":    resp.URL + "?" + v.Encode(),
			"query":  resp.Output,
		})
	} else {
		osin.OutputJSON(resp, c.Writer, c.Request)
	}
}

func (api *API) validateOauthRequest(c *gin.Context, ar *osin.AuthorizeRequest) bool {
	login := c.Request.FormValue("login")
	password := c.Request.FormValue("password")
	securityCode := c.Request.FormValue("securityCode")
	requestedScopes := strings.Split(c.Request.FormValue("scope"), ",")

	availableScopes, err := api.UserStore.Validate(login, password, securityCode)
	log.Println("Validating", login, password, securityCode, ":", err)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{})
		return false
	}

	if !util.ScopesAreAllowed(requestedScopes, availableScopes) {
		c.JSON(http.StatusUnauthorized, gin.H{})
		return false
	}

	ar.UserData = login

	return true
}

func (api *API) oauthAccessToken(c *gin.Context) {
	resp := api.OsinServer.NewResponse()
	defer resp.Close()

	c.Request.ParseForm()
	c.Request.Form.Set("grant_type", "authorization_code")

	if ar := api.OsinServer.HandleAccessRequest(resp, c.Request); ar != nil {
		ar.Authorized = true
		api.OsinServer.FinishAccessRequest(resp, c.Request, ar)
	}
	if resp.IsError && resp.InternalError != nil {
		fmt.Printf("ERROR: %s\n", resp.InternalError)
	}

	osin.OutputJSON(resp, c.Writer, c.Request)
}

func (api *API) getUser(c *gin.Context) {
	resp := api.OsinServer.NewResponse()
	defer osin.OutputJSON(resp, c.Writer, c.Request)

	var code string
	if token := osin.CheckBearerAuth(c.Request); token != nil {
		code = token.Code
	} else {
		code = c.Request.FormValue("access_token")
	}

	if code == "" {
		log.Println("No access token in request")
		resp.StatusCode = http.StatusUnauthorized
		return
	}

	accesstoken, err := api.OsinServer.Storage.LoadAccess(code)
	if err != nil {
		log.Println("Invalid accesstoken")
		resp.Output["error"] = "Bad Credentials"
		resp.StatusCode = http.StatusUnauthorized
		return
	}

	user, err := api.UserStore.Get(accesstoken.UserData.(string))
	if err != nil {
		log.Println("Unable to get user details:", err)
		resp.Output["error"] = "Internal Server Error"
		resp.StatusCode = http.StatusInternalServerError
		return
	}

	resp.Output["login"] = user.Login
	resp.Output["name"] = user.Name
	resp.Output["scopes"] = user.Scopes
	if len(user.Email) > 0 {
		resp.Output["email"] = user.Email[0]
	}
}
