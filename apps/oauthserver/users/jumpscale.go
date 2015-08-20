package users

import (
	"crypto/md5"
	"encoding/hex"
	"errors"
	"log"

	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/tfa"

	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
)

//JumpscaleStore implements the UserStore interface against a Jumpscale system
type JumpscaleStore struct {
	session *mgo.Session
}

//Get user profile information
func (store *JumpscaleStore) Get(username string) (ret *UserDetails, err error) {
	type user struct {
		ID     string
		Passwd string
		Emails []string
		Groups []string
	}
	var jumpscaleUser user
	collection := store.session.DB("js_system").C("user")
	err = collection.Find(bson.M{"id": username}).One(&jumpscaleUser)
	if err != nil {
		return
	}

	ret = &UserDetails{Login: username, Name: jumpscaleUser.ID, Email: jumpscaleUser.Emails, Scopes: jumpscaleUser.Groups}
	return
}

//Validate checks if a given password is correct for a username, it returns the groups it belongs to as scopes
func (store *JumpscaleStore) Validate(username, password, securityCode string) (scopes []string, err error) {
	type user struct {
		ID     string
		Passwd string
		Groups []string
	}
	var jumpscaleUser user
	collection := store.session.DB("js_system").C("user")
	err = collection.Find(bson.M{"id": username}).One(&jumpscaleUser)
	if err != nil {
		log.Print("Failed to load user ", username, " - ", err)
		return
	}

	hasher := md5.New()
	hasher.Write([]byte(password))
	md5hash := hasher.Sum(nil)

	md5hashedPassword := hex.EncodeToString(md5hash)
	if md5hashedPassword != jumpscaleUser.Passwd {
		err = InvalidPasswordError
		return
	}
	scopes = jumpscaleUser.Groups

	return
}

func (store *JumpscaleStore) SetTOTPSecret(username, secret string) error {
	return errors.New("Not implemented")
}

func (store *JumpscaleStore) GetTOTPSecret(username string) string {
	return ""
}

func (store *JumpscaleStore) SetRecovery(username string, recovery tfa.Recovery) error {
	return errors.New("Not implemented")
}

func (store *JumpscaleStore) GetRecovery(username string) (tfa.Recovery, bool) {
	return tfa.Recovery{}, false
}

//Close releases the mongo session
func (store *JumpscaleStore) Close() {
	store.session.Close()
}

//NewJumpscaleStore creates a new JumpscaleStore instance
func NewJumpscaleStore(connectionString string) (userStore *JumpscaleStore) {
	userStore = new(JumpscaleStore)
	session, err := mgo.Dial(connectionString)
	if err != nil {
		panic(err)
	}

	userStore.session = session
	return
}
