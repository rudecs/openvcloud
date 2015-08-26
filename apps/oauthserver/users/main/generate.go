package main

import (
	"fmt"
	"os"

	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/tfa"
	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/users/keyderivation"
)

func main() {
	if len(os.Args) == 1 {
		fmt.Fprintln(os.Stderr, "usage:", os.Args[0], "password pwd")
		fmt.Fprintln(os.Stderr, "      ", os.Args[0], "tfa")
		os.Exit(1)
	}

	command := os.Args[1]
	if command == "password" {
		if len(os.Args) != 3 {
			fmt.Fprintln(os.Stderr, "error: need 2 arguments")
		}
		key, salt := keyderivation.Hash(os.Args[2])
		fmt.Println("[users.{replace with username}.password]")
		fmt.Println("key = \"" + key + "\"")
		fmt.Println("salt = \"" + salt + "\"")

	} else if command == "tfa" {
		t := tfa.NewToken("", "")
		fmt.Println("[users.[replace with username].token]")
		fmt.Println("token = \"" + t.Base32() + "\"")
	}
}
