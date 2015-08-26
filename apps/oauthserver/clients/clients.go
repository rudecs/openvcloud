package clients

import (
	"errors"
	"net/http"

	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/util"

	"github.com/RangelReale/osin"
	"github.com/gin-gonic/gin"
)

type Store interface {
	ClientWithID(id string) *Client
}

type Client struct {
	*osin.DefaultClient
	Scopes []string
}

func RequireClient(c *gin.Context, clients Store) *Client {
	clientID := c.Request.Header.Get("X-Client-ID")
	clientSecret := c.Request.Header.Get("X-Client-Secret")
	if clientID == "" || clientSecret == "" {
		c.AbortWithError(http.StatusUnauthorized, errors.New("Client id or secret missing."))
		return nil
	}

	cl := clients.ClientWithID(clientID)
	if c == nil {
		c.AbortWithError(http.StatusUnauthorized, errors.New("Client "+clientID+"not found"))
		return nil
	}

	if clientSecret != cl.GetSecret() {
		c.AbortWithError(http.StatusUnauthorized, errors.New("Client secret did not match"))
		return nil
	}

	return cl
}

func RequireClientWithScopes(c *gin.Context, clients Store, scopes []string) *Client {
	cl := RequireClient(c, clients)
	if cl == nil {
		return nil
	}

	if !util.ScopesAreAllowed(scopes, cl.Scopes) {
		c.AbortWithError(http.StatusUnauthorized, errors.New("Scopes not allowed"))
		return nil
	}

	return cl
}
