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

type userData struct {
	Login string
}

func handleLoginPage(ar *osin.AuthorizeRequest, w http.ResponseWriter, r *http.Request, userStore users.UserStore) (validlogin bool) {
	r.ParseForm()
	data := struct {
		Error bool
	}{false}

	session, _ := cookiestore.Get(r, "openvcloudsession")
	if r.Method == "GET" {
		if !session.IsNew {
			username := session.Values["user"].(string)
			ar.UserData = userData{Login: username}
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
			ar.UserData = userData{Login: username}
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
	http.HandleFunc("/login/oauth/access_token", func(w http.ResponseWriter, r *http.Request) {
		resp := osinServer.NewResponse()
		defer resp.Close()

		//osin expects this to be set in the request
		//for compatibility with github oauht, set this
		r.ParseForm()
		r.Form.Set("grant_type", "authorization_code")

		if ar := osinServer.HandleAccessRequest(resp, r); ar != nil {
			ar.Authorized = true
			osinServer.FinishAccessRequest(resp, r, ar)
		}
		if resp.IsError && resp.InternalError != nil {
			fmt.Printf("ERROR: %s\n", resp.InternalError)
		}

		osin.OutputJSON(resp, w, r)
	})

	// User information
	http.HandleFunc("/user", func(w http.ResponseWriter, r *http.Request) {
		resp := osinServer.NewResponse()
		defer resp.Close()

		accesstoken, err := osinServer.Storage.LoadAccess(r.FormValue("access_token"))
		if err != nil {
			log.Println("Invalid accesstoken")
			return //TODO return the proper errormessage
		}

		user, err := userStore.Get(accesstoken.UserData.(userData).Login)
		if err != nil {
			log.Println("Unable to get user details", err)
			return //TODO return the proper errormessage
		}

		resp.Output["login"] = user.Login
		resp.Output["name"] = user.Name
		if len(user.Email) > 0 {
			resp.Output["email"] = user.Email[0]
		}
		osin.OutputJSON(resp, w, r)
	})

	log.Printf("Listening on %s\n", settings.Bind)
	http.ListenAndServe(settings.Bind, nil)
}
