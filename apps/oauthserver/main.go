package main

import (
	"fmt"
	"html/template"
	"io/ioutil"
	"log"
	"net/http"
	"os"

	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/keyderivation"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/storage"

	"github.com/RangelReale/osin"
	"github.com/gorilla/sessions"
	"github.com/naoina/toml"
)

var cookiestore *sessions.CookieStore

type settingsConfig struct {
	Bind              string
	CookieStoreSecret string
}

type authorizationsConfig struct {
	Users   map[string]user
	Clients map[string]osin.DefaultClient
}

type user struct {
	Email    string
	Name     string
	Password struct {
		Key  string
		Salt string
	}
}

func loadTomlFile(filename string, v interface{}) {
	f, err := os.Open(filename)
	if err != nil {
		panic(err)
	}
	defer f.Close()
	buf, err := ioutil.ReadAll(f)
	if err != nil {
		panic(err)
	}
	if err := toml.Unmarshal(buf, v); err != nil {
		panic(err)
	}
}

func handleLoginPage(ar *osin.AuthorizeRequest, w http.ResponseWriter, r *http.Request, users map[string]user) (validlogin bool) {
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
		if u, found := users[username]; found {
			password := r.FormValue("password")
			if keyderivation.Check(password, u.Password.Key, u.Password.Salt) {
				log.Printf("Authenticated %s ( %s )\n", username, u.Name)
				{
					session.Options.HttpOnly = true
					session.Options.MaxAge = 3600 * 12
					session.Values["user"] = username
					session.Save(r, w)
				}
				ar.UserData = struct {
					Login string
					Name  string
				}{Login: username, Name: u.Name}
				return true
			}
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
	loadTomlFile("settings.toml", &settings)

	var authorizations authorizationsConfig
	loadTomlFile("authorizations.toml", &authorizations)

	// Create the oauth configuration
	sconfig := osin.NewServerConfig()
	sconfig.AllowGetAccessRequest = true
	sconfig.AllowClientSecretInParams = true
	storagebackend := storage.NewSimpleStorage(authorizations.Clients)

	osinServer := osin.NewServer(sconfig, storagebackend)

	cookiestore = sessions.NewCookieStore([]byte(settings.CookieStoreSecret))

	//Handle authorize endpoint
	http.HandleFunc("/login/oauth/authorize", func(w http.ResponseWriter, r *http.Request) {
		resp := osinServer.NewResponse()
		defer resp.Close()

		if ar := osinServer.HandleAuthorizeRequest(resp, r); ar != nil {
			if !handleLoginPage(ar, w, r, authorizations.Users) {
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
