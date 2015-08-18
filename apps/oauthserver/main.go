package main

import (
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"strings"

	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/api"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/storage"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/util"

	"github.com/RangelReale/osin"
	"github.com/gin-gonic/contrib/static"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/handlers"
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

	requestedScopes := strings.Split(r.FormValue("scope"), ",")

	if r.Method == "GET" {
		if !session.IsNew {
			username := session.Values["user"].(string)
			ar.UserData = userData{Login: username}
			user, err := userStore.Get(username)
			if err != nil && util.ScopesAreAllowed(requestedScopes, user.Scopes) {
				return true
			}
		}
	}
	if r.Method == "POST" {
		username := r.FormValue("login")
		password := r.FormValue("password")
		availableScopes, err := userStore.Validate(username, password)
		if err == nil {
			if util.ScopesAreAllowed(requestedScopes, availableScopes) {
				session.Options.HttpOnly = true
				session.Options.MaxAge = 3600 * 12
				session.Values["user"] = username
				session.Save(r, w)
				ar.UserData = userData{Login: username}
				return true
			}
			log.Println("User does not have authorization on the requested scope")
		}

		data.Error = true
	}

	t, _ := template.ParseFiles("html/login.html")

	t.Execute(w, data)

	return
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

	var _ = osinServer

	// Start HTTP
	router := gin.Default()

	if _, err := os.Stat("html/"); err != nil {
		log.Fatal(err)
	}
	router.Use(static.Serve("/", static.LocalFile("static", true)))

	if err := api.New("/api", userStore).Install(router); err != nil {
		log.Fatal(err)
	}

	err := http.ListenAndServe(settings.Bind, router)
	if err != nil {
		log.Fatal(err)
	}
}

func oldMain() {
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
	http.Handle("/login/oauth/authorize", handlers.CombinedLoggingHandler(os.Stdout, http.HandlerFunc(
		func(w http.ResponseWriter, r *http.Request) {
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
		})))

	// Access token endpoint
	http.Handle("/login/oauth/access_token", handlers.CombinedLoggingHandler(os.Stdout, http.HandlerFunc(
		func(w http.ResponseWriter, r *http.Request) {
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
		})))

	// User information
	http.Handle("/user", handlers.CombinedLoggingHandler(os.Stdout, http.HandlerFunc(
		func(w http.ResponseWriter, r *http.Request) {
			resp := osinServer.NewResponse()
			defer osin.OutputJSON(resp, w, r)
			defer resp.Close()

			var code string
			if token := osin.CheckBearerAuth(r); token != nil {
				code = token.Code
			} else {
				code = r.FormValue("access_token")
			}

			if code == "" {
				log.Println("No access token in request")
				resp.Output["error"] = "Authorization Required"
				resp.StatusCode = 401
				return
			}

			accesstoken, err := osinServer.Storage.LoadAccess(code)
			if err != nil {
				log.Println("Invalid accesstoken")
				resp.Output["error"] = "Bad Credentials"
				resp.StatusCode = 401
				return
			}

			user, err := userStore.Get(accesstoken.UserData.(userData).Login)
			if err != nil {
				log.Println("Unable to get user details", err)
				resp.Output["error"] = "Internal Server Error"
				resp.StatusCode = 500
				return
			}

			resp.Output["login"] = user.Login
			resp.Output["name"] = user.Name
			resp.Output["scopes"] = user.Scopes
			if len(user.Email) > 0 {
				resp.Output["email"] = user.Email[0]
			}
		})))

	http.Handle("/logout", handlers.CombinedLoggingHandler(os.Stdout, http.HandlerFunc(
		func(w http.ResponseWriter, r *http.Request) {
			r.ParseForm()
			redirectURI := r.Form.Get("redirect_uri")

			session, _ := cookiestore.Get(r, "openvcloudsession")
			//invalidate the session by setting age to -1
			session.Options.MaxAge = -1

			session.Save(r, w)

			if redirectURI != "" {
				http.Redirect(w, r, redirectURI, 302)
			}
		})))

	log.Printf("Listening on %s\n", settings.Bind)
	http.ListenAndServe(settings.Bind, nil)
}
