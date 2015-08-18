package api

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func (api *API) validateLoginPassword(c *gin.Context) {
	var validationRequest struct {
		Login    string `json:"login" binding:"required"`
		Password string `json:"password" binding:"required"`
	}

	if err := c.BindJSON(&validationRequest); err != nil {
		c.AbortWithError(http.StatusBadRequest, err)
		return
	}

	_, status := api.UserStore.Validate(validationRequest.Login, validationRequest.Password)

	if status == nil {
		c.JSON(http.StatusOK, gin.H{"status": "tfa_required"})
	} else {
		c.JSON(http.StatusOK, gin.H{"status": "invalid"})
	}
}
