package main

import (
	"log"
	"net/http"
	"os"

	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/api"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/storage"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/util"

	"github.com/RangelReale/osin"
	"github.com/gin-gonic/contrib/static"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/sessions"
)

var cookiestore *sessions.CookieStore

type settingsConfig struct {
	Bind              string
	CookieStoreSecret string
	Jumpscale         struct {
		Mongo struct {
			Connectionstring string
		}
	}
}

func main() {
	// Load the settings
	var settings settingsConfig
	util.LoadTomlFile("settings.toml", &settings)

	var clients struct {
		Clients []osin.DefaultClient
	}
	util.LoadTomlFile("clients.toml", &clients)

	// Create the oauth configuration
	sconfig := osin.NewServerConfig()
	sconfig.AllowGetAccessRequest = true
	sconfig.AllowClientSecretInParams = true
	storagebackend := storage.NewSimpleStorage(clients.Clients)

	osinServer := osin.NewServer(sconfig, storagebackend)
	var userStore users.UserStore
	if settings.Jumpscale.Mongo.Connectionstring != "" {
		userStore = users.NewJumpscaleStore(settings.Jumpscale.Mongo.Connectionstring)
	} else {
		userStore = users.NewTomlStore("users.toml")
	}
	defer userStore.Close()

	cookiestore = sessions.NewCookieStore([]byte(settings.CookieStoreSecret))

	// Start HTTP
	router := gin.Default()

	if _, err := os.Stat("static/"); err != nil {
		log.Fatal(err)
	}
	router.Use(static.Serve("/", static.LocalFile("static", true)))
	router.Static("/login/oauth/authorize", "static/")

	if err := api.New(userStore, osinServer).Install(router); err != nil {
		log.Fatal(err)
	}

	err := http.ListenAndServe(settings.Bind, router)
	if err != nil {
		log.Fatal(err)
	}
}
