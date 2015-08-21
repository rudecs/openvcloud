package main

import (
	"html/template"
	"log"
	"net/http"
	"os"
	"strings"

	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/api"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/clients"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/storage"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/util"

	"github.com/RangelReale/osin"
	"github.com/gin-gonic/contrib/static"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/context"
	"github.com/gorilla/sessions"
)

var cookiestore *sessions.CookieStore
var userStore users.UserStore
var osinServer *osin.Server

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
		Clients []clients.Client
	}
	util.LoadTomlFile("clients.toml", &clients)

	// Create the oauth configuration
	sconfig := osin.NewServerConfig()
	sconfig.AllowGetAccessRequest = true
	sconfig.AllowClientSecretInParams = true
	storagebackend := storage.NewSimpleStorage(clients.Clients)

	osinServer = osin.NewServer(sconfig, storagebackend)
	if settings.Jumpscale.Mongo.Connectionstring != "" {
		userStore = users.NewJumpscaleStore(settings.Jumpscale.Mongo.Connectionstring)
	} else {
		userStore = users.NewTomlStore("users.toml")
	}
	defer userStore.Close()

	cookiestore = sessions.NewCookieStore([]byte(settings.CookieStoreSecret))

	// Start HTTP
	router := gin.Default()

	if _, err := os.Stat("html/"); err != nil {
		log.Fatal(err)
	}
	router.Use(static.Serve("/", static.LocalFile("html", true)))
	router.GET("/login/oauth/authorize", loginPage)

	if err := api.New(userStore, osinServer, cookiestore).Install(router); err != nil {
		log.Fatal(err)
	}

	err := http.ListenAndServe(settings.Bind, context.ClearHandler(router))
	if err != nil {
		log.Fatal(err)
	}
}

func loginPage(c *gin.Context) {
	session, _ := cookiestore.Get(c.Request, "openvcloudsession")
	requestedScopes := strings.Split(c.Request.FormValue("scope"), ",")

	resp := osinServer.NewResponse()
	defer resp.Close()

	if v := session.Values["user"]; v != nil {
		if username, flag := v.(string); flag {
			u, err := userStore.Get(username)
			if err == nil && util.ScopesAreAllowed(requestedScopes, u.Scopes) {
				if ar := osinServer.HandleAccessRequest(resp, c.Request); ar != nil {
					log.Println("Ha!")
					ar.Authorized = true
					ar.UserData = username
					osinServer.FinishAccessRequest(resp, c.Request, ar)
					osin.OutputJSON(resp, c.Writer, c.Request)
					resp.Close()
					return
				}
			}
		}
	}

	t, _ := template.ParseFiles("html/login.html")
	t.Execute(c.Writer, nil)
}
