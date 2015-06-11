package main

import (
	"fmt"
	"html/template"
	"log"
	"net/http"

	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/storage"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/util"

	"github.com/RangelReale/osin"
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

func handleLoginPage(ar *osin.AuthorizeRequest, w http.ResponseWriter, r *http.Request, userStore users.UserStore) (validlogin bool) {
	r.ParseForm()
	data := struct {
		Error bool
	}{false}

	session, _ := cookiestore.Get(r, "openvcloudsession")
	if r.Method == "GET" {
		if !session.IsNew {
			return true
		}
	}
	if r.Method == "POST" {
		username := r.FormValue("login")
		password := r.FormValue("password")
		if userStore.Validate(username, password) {
			log.Printf("Authenticated %s\n", username)
			{
				session.Options.HttpOnly = true
				session.Options.MaxAge = 3600 * 12
				session.Values["user"] = username
				session.Save(r, w)
			}
			ar.UserData = struct {
				Login string
				Name  string
			}{Login: username}
			return true
		}

		data.Error = true
	}

	t, _ := template.ParseFiles("html/login.html")

	t.Execute(w, data)

	return
}

func main() {
	//Load the settings
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

	//Handle authorize endpoint
	http.HandleFunc("/login/oauth/authorize", func(w http.ResponseWriter, r *http.Request) {
		resp := osinServer.NewResponse()
		defer resp.Close()

		if ar := osinServer.HandleAuthorizeRequest(resp, r); ar != nil {
			if !handleLoginPage(ar, w, r, userStore) {
				return
			}
			ar.Authorized = true
			osinServer.FinishAuthorizeRequest(resp, r, ar)
		}
		if resp.IsError && resp.InternalError != nil {
			fmt.Printf("ERROR: %s\n", resp.InternalError)
		}
		osin.OutputJSON(resp, w, r)
	})

	// Access token endpoint
	http.HandleFunc("/login/oauth/token", func(w http.ResponseWriter, r *http.Request) {
		resp := osinServer.NewResponse()
		defer resp.Close()

		if ar := osinServer.HandleAccessRequest(resp, r); ar != nil {
			switch ar.Type {
			case osin.AUTHORIZATION_CODE:
				ar.Authorized = true
			case osin.REFRESH_TOKEN:
				ar.Authorized = true
			}
			osinServer.FinishAccessRequest(resp, r, ar)
		}
		if resp.IsError && resp.InternalError != nil {
			fmt.Printf("ERROR: %s\n", resp.InternalError)
		}

		osin.OutputJSON(resp, w, r)
	})

	log.Printf("Listening on %s\n", settings.Bind)
	http.ListenAndServe(settings.Bind, nil)
}
