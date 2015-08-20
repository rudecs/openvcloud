package api

import (
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users"
	"github.com/RangelReale/osin"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/sessions"
)

func (api *API) Install(router *gin.Engine) error {
	// login
	router.POST("/api/login/validate", api.validateLogin)
	router.POST("/api/oauth/validate", api.validateOauth)
	router.POST("/login/oauth/access_token", api.oauthAccessToken)
	router.GET("/user", api.getUser)

	// tfa
	router.POST("/api/tfa/token/update", api.updateToken)
	router.GET("/api/tfa/token/enabled", api.isTokenEnabled)
	router.POST("/api/tfa/token/delete", api.deleteToken)
	router.GET("/api/tfa/recovery", api.getRecoveryCodes)
	router.POST("/api/tfa/recovery/renew", api.renewRecoveryCodes)

	return nil
}

type API struct {
	UserStore   users.UserStore
	OsinServer  *osin.Server
	CookieStore *sessions.CookieStore
}

func New(userStore users.UserStore, osinServer *osin.Server, cookiestore *sessions.CookieStore) *API {
	return &API{
		UserStore:   userStore,
		OsinServer:  osinServer,
		CookieStore: cookiestore,
	}
}
