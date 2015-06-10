package keyderivation

import (
	"crypto/rand"

	"golang.org/x/crypto/pbkdf2"
	"golang.org/x/crypto/ripemd160"
)

//Hash creates a random 16 byte salt and creates a 64 byte key
//Key generation function: RIPEMD160 based PBKDF2 key derivation with 2000 iterations
//The key and salt are returned as base58 encoded strings
func Hash(password string) (key, salt string) {
	rawsalt := generateSalt()
	rawkey := hash(password, rawsalt)
	salt = EncodeBase58(rawsalt)
	key = EncodeBase58(rawkey)
	return
}

func hash(password string, salt []byte) (key []byte) {
	key = pbkdf2.Key([]byte(password), salt, 2000, 64, ripemd160.New)
	return
}

//Check takes the password and the base58 encoded key and salt
// and checks if the combination matches
func Check(password, key, salt string) bool {
	rawsalt := DecodeBase58(salt)
	rawkey := hash(password, rawsalt)
	generatedKey := EncodeBase58(rawkey)
	return key == generatedKey
}

func generateSalt() (salt []byte) {
	salt = make([]byte, 16)
	_, err := rand.Read(salt)
	if err != nil {
		panic(err)
	}
	return
}
