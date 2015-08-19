package api

import (
	"net/http"

	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users"

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
