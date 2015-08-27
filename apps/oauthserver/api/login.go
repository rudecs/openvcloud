package api

import (
	"fmt"
	"net/http"
	"net/url"
	"strings"

	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/util"

	"github.com/RangelReale/osin"
	"github.com/gin-gonic/gin"
)

func (api *API) authorizeOauth(c *gin.Context) {
	var r struct {
		Login        string `json:"login" binding:"required"`
		Password     string `json:"password" binding:"required"`
		SecurityCode string `json:"securityCode"`
	}

	c.Request.ParseForm()

	r.Login = c.Request.FormValue("login")
	r.Password = c.Request.FormValue("password")
	r.SecurityCode = c.Request.FormValue("securityCode")

	_, status := api.UserStore.Validate(r.Login, r.Password, r.SecurityCode, false)

	if status == nil {
		api.validateOauth(c)

	} else if status == users.InvalidPasswordError || status == users.UserNotFoundError {
		c.JSON(http.StatusUnauthorized, gin.H{"status": "invalid_password"})
	} else if status == users.InvalidSecurityCodeError {
		c.JSON(http.StatusUnauthorized, gin.H{"status": "invalid_security_code"})
	} else {
		c.AbortWithError(http.StatusInternalServerError, status)
	}
}

func (api *API) validateOauth(c *gin.Context) {
	resp := api.OsinServer.NewResponse()
	defer resp.Close()

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

	session, _ := api.CookieStore.Get(c.Request, "openvcloudsession")
	session.Values["user"] = c.Request.FormValue("login")
	session.Save(c.Request, c.Writer)

	if resp.Type == osin.REDIRECT {
		v := url.Values{}
		if s := resp.Output["code"].(string); s != "" {
			v.Set("code", s)
		}
		if s := resp.Output["state"].(string); s != "" {
			v.Set("state", s)
		}

		if c.Request.Header.Get("Accept") == "application/json" {
			c.JSON(http.StatusOK, gin.H{
				"status": "ok",
				"url":    resp.URL + "?" + v.Encode(),
			})
		} else {
			osin.OutputJSON(resp, c.Writer, c.Request)
		}
	} else {
		osin.OutputJSON(resp, c.Writer, c.Request)
	}
}

func (api *API) validateOauthRequest(c *gin.Context, ar *osin.AuthorizeRequest) bool {
	login := c.Request.FormValue("login")
	password := c.Request.FormValue("password")
	securityCode := c.Request.FormValue("securityCode")
	requestedScopes := strings.Split(c.Request.FormValue("scope"), ",")

	availableScopes, err := api.UserStore.Validate(login, password, securityCode, true)
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
	user := users.RequiresUser(c, api.OsinServer, api.UserStore)
	if user == nil {
		return
	}

	resp := api.OsinServer.NewResponse()
	defer osin.OutputJSON(resp, c.Writer, c.Request)

	resp.Output["login"] = user.Login
	resp.Output["name"] = user.Name
	resp.Output["scopes"] = user.Scopes
	if len(user.Email) > 0 {
		resp.Output["email"] = user.Email[0]
	}
}