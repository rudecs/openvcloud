package api

import (
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users"
	"github.com/RangelReale/osin"
	"github.com/gin-gonic/gin"
)

func (api *API) Install(router *gin.Engine) error {
	router.POST(api.Prefix+"/login/validate", api.validateLogin)
	router.POST(api.Prefix+"/oauth/validate", api.validateOauth)
	return nil
}

type API struct {
	Prefix     string
	UserStore  users.UserStore
	OsinServer *osin.Server
}

func New(prefix string, userStore users.UserStore, osinServer *osin.Server) *API {
	return &API{
		Prefix:     prefix,
		UserStore:  userStore,
		OsinServer: osinServer,
	}
}
