package users

import (
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users/keyderivation"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/util"
	"github.com/RangelReale/osin"
)

//TomlStore implements the UserStore interface for a local file
type TomlStore struct {
	users map[string]user
}

//Validate checks if a given password is correct for a username
func (store *TomlStore) Validate(username, password string) (match bool) {
	if u, found := store.users[username]; found {
		return keyderivation.Check(password, u.Password.Key, u.Password.Salt)
	}
	return
}

//NewTomlStore creates a new TomlStore instance and loads the users from a local file
func NewTomlStore(filename string) (userStore *TomlStore) {
	userStore = new(TomlStore)

	var data struct {
		Users map[string]user
	}

	util.LoadTomlFile(filename, &data)
	userStore.users = data.Users

	return
}

type user struct {
	Email    string
	Name     string
	Password struct {
		Key  string
		Salt string
	}
}

type authorizationsConfig struct {
	Users   map[string]user
	Clients []osin.DefaultClient
}
