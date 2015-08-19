package api

import (
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users"
	"github.com/RangelReale/osin"
	"github.com/gin-gonic/gin"
)

func (api *API) Install(router *gin.Engine) error {
	router.POST("/api/login/validate", api.validateLogin)
	router.POST("/api/oauth/validate", api.validateOauth)
	return nil
}

type API struct {
	UserStore  users.UserStore
	OsinServer *osin.Server
}

func New(userStore users.UserStore, osinServer *osin.Server) *API {
	return &API{
		UserStore:  userStore,
		OsinServer: osinServer,
	}
}
