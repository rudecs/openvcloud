package users

import (
	"encoding/base32"
	"log"

	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/tfa"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users/keyderivation"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/util"
)

//TomlStore implements the UserStore interface for a local file
type TomlStore struct {
	users map[string]user
	dirty chan bool
}

//Get user profile information
func (store *TomlStore) Get(username string) (ret *UserDetails, err error) {
	if u, found := store.users[username]; found {
		ret = &UserDetails{Login: username, Name: u.Name, Email: []string{u.Email}, Scopes: u.Scopes}
		return
	}
	err = UserNotFoundError
	return
}

//Validate checks if a given password is correct for a username
func (store *TomlStore) Validate(username, password, securityCode string) (scopes []string, err error) {

	u, found := store.users[username]
	if !found {
		err = UserNotFoundError
		return
	}
	if !keyderivation.Check(password, u.Password.Key, u.Password.Salt) {
		err = InvalidPasswordError
		return
	}

	log.Println("For user token:", u.TFA.Token)
	if u.TFA.Token != "" {
		secret, e := base32.StdEncoding.DecodeString(u.TFA.Token)
		if e != nil {
			err = e
			return
		}

		t := &tfa.Token{Secret: secret}
		totp := t.TOTP()
		log.Println("->", totp.Now().Get(), "=", securityCode)
		if !totp.Now().Verify(securityCode) {
			err = InvalidSecurityCodeError
			return
		}
	}
	scopes = u.Scopes
	return
}

func (store *TomlStore) SetTOTPSecret(username, secret string) error {
	u, ok := store.users[username]
	if !ok {
		return UserNotFoundError
	}

	log.Println("Updating to", secret)
	u.TFA.Token = secret
	store.users[username] = u
	store.dirty <- true

	return nil
}

func (store *TomlStore) GetTOTPSecret(username string) string {
	u, ok := store.users[username]
	if !ok {
		return ""
	}

	return u.TFA.Token
}

func (store *TomlStore) SetRecovery(username string, recovery tfa.Recovery) error {
	u, ok := store.users[username]
	if !ok {
		return UserNotFoundError
	}

	u.TFA.Recovery = recovery
	store.users[username] = u
	store.dirty <- true

	return nil
}

func (store *TomlStore) GetRecovery(username string) (tfa.Recovery, bool) {
	u, ok := store.users[username]
	if !ok {
		return tfa.Recovery{}, false
	}

	return u.TFA.Recovery, true
}

//NewTomlStore creates a new TomlStore instance and loads the users from a local file
func NewTomlStore(filename string) (userStore *TomlStore) {
	userStore = new(TomlStore)

	var data struct {
		Users map[string]user
	}

	util.LoadTomlFile(filename, &data)
	userStore.users = data.Users

	userStore.dirty = make(chan bool)
	go func() {
		for {
			<-userStore.dirty
			var data struct {
				Users map[string]user
			}
			data.Users = userStore.users
			util.WriteTomlFile(filename, data)
		}
	}()

	return
}

//Close does nothing since we don't hold any resources
func (store *TomlStore) Close() {
}

type user struct {
	Email    string
	Name     string
	Scopes   []string
	Password struct {
		Key  string
		Salt string
	}
	TFA struct {
		Token    string
		Recovery tfa.Recovery
	}
}
