package main

import (
	"fmt"
	"os"

	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users/keyderivation"
)

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "usage:", os.Args[0], "password")
		os.Exit(1)
	}

	key, salt := keyderivation.Hash(os.Args[1])
	fmt.Println("key = \"" + key + "\"")
	fmt.Println("salt = \"" + salt + "\"")
}
