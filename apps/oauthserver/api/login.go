package api

import (
	"net/http"

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
		c.JSON(http.StatusOK, gin.H{"status": "tfa_required"})
	} else {
		c.JSON(http.StatusOK, gin.H{"status": "invalid_password"})
	}
}
