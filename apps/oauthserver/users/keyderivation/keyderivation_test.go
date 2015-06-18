package keyderivation

import (
	"fmt"
	"testing"
)

func TestHash(t *testing.T) {
	password := "MySuperSecretPassword"
	fmt.Println("Password: ", password)
	key, salt := Hash(password)
	fmt.Println("Key: ", key)
	fmt.Println("Generated salt: ", salt)
}

func TestCheck(t *testing.T) {
	password := "MySuperSecretPassword"
	salt := "87Sv37viXVe4qvDhBxWMy9"
	key := "2Gd2Y1n17rBRXX1qukj4anQbz3UtXo2L65KjLhasbvkx2omTUPKVyLjqB5A4tcpE58i8osYNVQqJLqj112hxuPva"
	if !Check(password, key, salt) {
		t.Error("Password and salt should match the given key")
	}
}
