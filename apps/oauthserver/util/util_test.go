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
