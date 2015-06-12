package users

import (
	"crypto/md5"
	"encoding/hex"
	"log"

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
	}
	var jumpscaleUser user
	collection := store.session.DB("js_system").C("user")
	err = collection.Find(bson.M{"id": username, "domain": "jumpscale"}).One(&jumpscaleUser)
	if err != nil {
		return
	}

	ret = &UserDetails{Login: username, Name: jumpscaleUser.ID, Email: jumpscaleUser.Emails}
	return
}

//Validate checks if a given password is correct for a username
func (store *JumpscaleStore) Validate(username, password string) (match bool) {
	type user struct {
		ID     string
		Passwd string
	}
	var jumpscaleUser user
	collection := store.session.DB("js_system").C("user")
	err := collection.Find(bson.M{"id": username, "domain": "jumpscale"}).One(&jumpscaleUser)
	if err != nil {
		log.Print("Failed to load user ", username, " - ", err)
		return
	}

	hasher := md5.New()
	hasher.Write([]byte(password))
	md5hash := hasher.Sum(nil)

	md5hashedPassword := hex.EncodeToString(md5hash)
	return md5hashedPassword == jumpscaleUser.Passwd
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
