package tfa

import (
	"encoding/base64"
	"encoding/json"
	"log"
	"os"
	"time"

	"github.com/pmylund/go-cache"
)

var generatedTokens = cache.New(15*time.Minute, 1*time.Minute)

func GenerateToken(user string) Token {
	t := NewToken(Provider, user)
	generatedTokens.Set(user, t, cache.DefaultExpiration)
	return t
}

func GetGeneratedToken(user string) (Token, bool) {
	o, ok := generatedTokens.Get(user)
	if !ok {
		return Token{}, false
	}

	return o.(Token), true
}

func DeleteGeneratedToken(user string) {
	generatedTokens.Delete(user)
}

var tokensInUseDirty = make(chan bool, 1)
var tokensInUse *cache.Cache

func SetToken(user string, token Token) {
	tokensInUse.Set(user, token, cache.DefaultExpiration)

	tokensInUseDirty <- true
}

func GetToken(user string) (Token, bool) {
	o, ok := tokensInUse.Get(user)
	if !ok {
		return Token{}, false
	}

	return o.(Token), true
}

func DeleteToken(user string) {
	tokensInUse.Delete(user)
	tokensInUseDirty <- true
}

var recoveryCodesDirty = make(chan bool, 1)
var recoveryCodes *cache.Cache

func GetRecovery(user string) (Recovery, bool) {
	o, ok := recoveryCodes.Get(user)
	if !ok {
		return Recovery{}, false
	}

	return o.(Recovery), true
}

func SetRecovery(user string, r Recovery) {
	recoveryCodes.Set(user, r, cache.NoExpiration)
	recoveryCodesDirty <- true
}

func init() {
	// Of course this should be changed to a real database

	// Load shared secrets
	tokens_filename := "tfa_tokens.json"

	fh, err := os.Open(tokens_filename)
	log.Println("Loading TFA tokens from", tokens_filename)
	if err != nil {
		log.Println("Could not load TFA tokens, using empty cache:", err)
		tokensInUse = cache.New(cache.NoExpiration, cache.NoExpiration)

	} else {
		defer fh.Close()

		items := make(map[string]*cache.Item, 0)
		if err := json.NewDecoder(fh).Decode(&items); err != nil {
			log.Fatal("Could not load TFA tokens:", err)
		}

		for _, i := range items {
			o := i.Object.(map[string]interface{})

			secret, err := base64.StdEncoding.DecodeString(o["Secret"].(string))
			if err != nil {
				log.Fatalln("Could not decode secret:", o["Secret"], ":", err)
			}
			i.Object = Token{
				Provider: o["Provider"].(string),
				User:     o["User"].(string),
				Secret:   secret,
			}
		}

		tokensInUse = cache.NewFrom(cache.NoExpiration, cache.NoExpiration, items)
	}

	// Load recovery codes
	recovery_filename := "tfa_recovery.json"

	fh, err = os.Open(recovery_filename)
	log.Println("Loading TFA recovery codes from", recovery_filename)
	if err != nil {
		log.Println("Could not load TFA recovery codes, using empty cache:", err)
		recoveryCodes = cache.New(cache.NoExpiration, cache.NoExpiration)

	} else {
		defer fh.Close()

		items := make(map[string]Recovery)
		if err := json.NewDecoder(fh).Decode(&items); err != nil {
			log.Fatal("Could not load TFA recovery codes:", err)
		}

		converted := make(map[string]*cache.Item, len(items))
		for key, value := range items {
			converted[key] = &cache.Item{
				Object: value,
			}
		}

		recoveryCodes = cache.New(cache.NoExpiration, cache.NoExpiration)
	}

	// Periodically save
	go func() {
		for {
			<-tokensInUseDirty

			items := tokensInUse.Items()
			fh, err := os.Create(tokens_filename)
			if err != nil {
				log.Println("Could not save TFA tokens:", err)
				continue
			}
			defer fh.Close()

			if err := json.NewEncoder(fh).Encode(items); err != nil {
				log.Println("Could not save TFA tokens:", err)
				continue
			}
		}
	}()

	go func() {
		for {
			<-recoveryCodesDirty

			items := recoveryCodes.Items()
			converted := make(map[string]Recovery)
			for key, value := range items {
				converted[key] = value.Object.(Recovery)
			}

			fh, err := os.Create(recovery_filename)
			if err != nil {
				log.Println("Could not save TFA recovery codes:", err)
				continue
			}
			defer fh.Close()

			if err := json.NewEncoder(fh).Encode(converted); err != nil {
				log.Println("Could not save TFA recovery codes:", err)
				continue
			}
		}
	}()
}
