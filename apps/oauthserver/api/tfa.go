package api

import (
	"encoding/base32"
	"net/http"

	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/clients"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/tfa"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users"
	"github.com/gin-gonic/gin"
)

func (api *API) updateToken(c *gin.Context) {
	user := users.RequiresUser(c, api.OsinServer, api.UserStore)
	if user == nil {
		return
	}

	if clients.RequireClientWithScopes(c, api.ClientStore, []string{clients.WriteUserCredentialsScope}) == nil {
		return
	}

	var r struct {
		Secret string `json:"secret" binding:"required"` // Base32 encoded
	}
	if err := c.BindJSON(&r); err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
		return
	}

	if _, err := base32.StdEncoding.DecodeString(r.Secret); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Not a Base32 encoded value"})
		return
	}

	if err := api.UserStore.SetTOTPSecret(user.Login, r.Secret); err != nil {
		c.AbortWithError(http.StatusInternalServerError, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{})
}

func (api *API) isTokenEnabled(c *gin.Context) {
	user := users.RequiresUser(c, api.OsinServer, api.UserStore)
	if user == nil {
		return
	}

	if clients.RequireClientWithScopes(c, api.ClientStore, []string{clients.ReadUserCredentialsScope}) == nil {
		return
	}

	if api.UserStore.GetTOTPSecret(user.Login) == "" {
		c.JSON(http.StatusOK, gin.H{"status": "disabled"})
	} else {
		c.JSON(http.StatusOK, gin.H{"status": "enabled"})
	}
}

func (api *API) deleteToken(c *gin.Context) {
	user := users.RequiresUser(c, api.OsinServer, api.UserStore)
	if user == nil {
		return
	}

	if clients.RequireClientWithScopes(c, api.ClientStore, []string{clients.WriteUserCredentialsScope}) == nil {
		return
	}

	if err := api.UserStore.SetTOTPSecret(user.Login, ""); err != nil {
		c.AbortWithError(http.StatusInternalServerError, err)
		return
	}

	c.JSON(http.StatusOK, gin.H{})
}

func (api *API) getRecoveryCodes(c *gin.Context) {
	user := users.RequiresUser(c, api.OsinServer, api.UserStore)
	if user == nil {
		return
	}

	if clients.RequireClientWithScopes(c, api.ClientStore, []string{clients.WriteUserCredentialsScope}) == nil {
		return
	}

	if api.UserStore.GetTOTPSecret(user.Login) == "" {
		c.JSON(http.StatusNotFound, gin.H{
			"reason": "TFA is disabled for this user",
		})
		return
	}

	s, ok := api.UserStore.GetRecovery(user.Login)
	if !ok {
		s = tfa.Recovery{}
		s.GenerateCodes()
		api.UserStore.SetRecovery(user.Login, s)
	}
	c.JSON(http.StatusOK, s)
}

func (api *API) renewRecoveryCodes(c *gin.Context) {
	user := users.RequiresUser(c, api.OsinServer, api.UserStore)
	if user == nil {
		return
	}

	if clients.RequireClientWithScopes(c, api.ClientStore, []string{clients.WriteUserCredentialsScope}) == nil {
		return
	}

	if api.UserStore.GetTOTPSecret(user.Login) == "" {
		c.JSON(http.StatusNotFound, gin.H{
			"reason": "TFA is disabled for this user",
		})
		return
	}

	r := tfa.Recovery{}
	r.GenerateCodes()
	api.UserStore.SetRecovery(user.Login, r)

	c.JSON(http.StatusOK, gin.H{})
}
