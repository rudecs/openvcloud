package util

import (
	"io/ioutil"
	"os"
	"testing"
)

func TestLoadTomlFile(t *testing.T) {
	type testData struct{ Prop string }

	tempfile, _ := ioutil.TempFile("", "")
	tempfile.WriteString("prop = \"test\"\n")
	tempfile.Close()
	defer os.Remove(tempfile.Name())

	var loadedData testData
	LoadTomlFile(tempfile.Name(), &loadedData)
	if loadedData.Prop != "test" {
		t.Error("Something went wrong loading the toml file")
	}
}

func TestScopesAreAllowed(t *testing.T) {
	allowedScopes := []string{"user", "ovs:admin"}
	requestedScopes := []string{"ovs:admin "}
	if !ScopesAreAllowed(requestedScopes, allowedScopes) {
		t.Error("The requested scopes should be allowed\nRequested:", requestedScopes, "\nAllowed:", allowedScopes)
	}
	requestedScopes = []string{"ovs:admin", "grid:admin"}
	if ScopesAreAllowed(requestedScopes, allowedScopes) {
		t.Error("The requested scopes should be not allowed\nRequested:", requestedScopes, "\nAllowed:", allowedScopes)
	}
}
