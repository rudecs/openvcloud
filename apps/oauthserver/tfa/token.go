package tfa

import (
	"crypto/rand"
	"encoding/base32"
	"fmt"
	"math/big"

	"github.com/hgfischer/go-otp"

	"code.google.com/p/rsc/qr"
)

type Token struct {
	Provider string
	User     string
	Secret   []byte
}

func NewToken(provider, user string) Token {
	return Token{
		Provider: provider,
		User:     user,
		Secret:   generateRandomBytes(TokenLength),
	}
}

func (token *Token) TOTPURL() string {
	var p string
	if token.Provider == "" {
		p = ""
	} else {
		p = token.Provider + ":"
	}

	return fmt.Sprintf(
		"otpauth://totp/%s%s?secret=%s",
		p,
		token.User,
		token.Base32(),
	)
}

func (token *Token) TOTP() otp.TOTP {
	return otp.TOTP{
		Secret:         token.Base32(),
		IsBase32Secret: true,
	}
}

func (token *Token) Base32() string {
	return base32.StdEncoding.EncodeToString(token.Secret)

}

func (token *Token) QRCode() (*qr.Code, error) {
	return qr.Encode(token.TOTPURL(), qr.L)
}

func (token *Token) PNG() ([]byte, error) {
	c, err := token.QRCode()
	if err != nil {
		return nil, err
	}

	return c.PNG(), nil
}

func generateRandomBytes(length int) []byte {
	b := make([]byte, length)
	_, err := rand.Read(b)
	if err != nil {
		panic(err)
	}
	return b
}

func generateRandomString(symbols []rune, length int) string {
	n := big.NewInt(int64(len(symbols)))
	b := make([]rune, length)
	for i := range b {
		r, err := rand.Int(rand.Reader, n)
		if err != nil {
			panic(err)
		}
		b[i] = symbols[int(r.Int64())]
	}
	return string(b)
}
