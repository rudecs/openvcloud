package util

import (
	"io/ioutil"
	"os"
	"strings"

	"github.com/BurntSushi/toml"
)

//LoadTomlFile loads toml using "github.com/naoina/toml"
func LoadTomlFile(filename string, v interface{}) {
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

func WriteTomlFile(filename string, v interface{}) {
	f, err := os.Create(filename)
	if err != nil {
		panic(err)
	}
	defer f.Close()

	if err := toml.NewEncoder(f).Encode(v); err != nil {
		panic(err)
	}
}

func contains(value string, collection []string) bool {
	for _, v := range collection {
		if value == v {
			return true
		}
	}
	return false
}

//ScopesAreAllowed checks if the requestedScopes are a subset of the allowedScopes
//Pretty naive implementation for now, does not check child scopes (like user:email)
func ScopesAreAllowed(requestedScopes, allowedScopes []string) bool {
	for _, s := range requestedScopes {
		if !contains(strings.TrimSpace(s), allowedScopes) {
			return false
		}
	}
	return true
}
