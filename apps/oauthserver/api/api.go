package api

import (
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users"
	"github.com/gin-gonic/gin"
)

func (api *API) Install(router *gin.Engine) error {
	router.POST(api.Prefix+"/login/validate", api.validateLogin)

	return nil
}

type API struct {
	Prefix    string
	UserStore users.UserStore
}

func New(prefix string, userStore users.UserStore) *API {
	return &API{
		Prefix:    prefix,
		UserStore: userStore,
	}
}
