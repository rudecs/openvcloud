package clients

import "github.com/RangelReale/osin"

type Client struct {
	*osin.DefaultClient
	Scopes []string
}
