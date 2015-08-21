package storage

import (
	"errors"
	"time"

	"git.aydo.com/0-complexity/openvcloud/apps/oauthserver/clients"

	"github.com/RangelReale/osin"
	"github.com/pmylund/go-cache"
)

//SimpleStorage is an in-memory storage backend for osin
type SimpleStorage struct {
	clients   map[string]clients.Client
	authorize *cache.Cache
	access    *cache.Cache
	refresh   *cache.Cache
}

//MaxCacheEntries limits the number of cached authorization and access tokens
//It would be a little to easy to trash the system if this was not present
const MaxCacheEntries = 20000

//NewSimpleStorage creates and initializes a SimpleStorage instance
func NewSimpleStorage(cls []clients.Client) *SimpleStorage {
	r := &SimpleStorage{
		clients:   make(map[string]clients.Client),
		authorize: cache.New(1*time.Minute, 10*time.Second),
		access:    cache.New(1*time.Minute, 30*time.Second),
		refresh:   cache.New(1*time.Minute, 30*time.Second),
	}
	for i := range cls {
		client := cls[i]
		r.clients[client.Id] = client
	}

	return r
}

// Clone the storage if needed. For example, using mgo, you can clone the session with session.Clone
// to avoid concurrent access problems.
// This is to avoid cloning the connection at each method access.
// Can return itself if not a problem.
func (s *SimpleStorage) Clone() osin.Storage {
	return s
}

// Close the resources the Storage potentially holds (using Clone for example)
func (s *SimpleStorage) Close() {
}

// GetClient loads the client by id (client_id)
func (s *SimpleStorage) GetClient(id string) (osin.Client, error) {
	if c, ok := s.clients[id]; ok {
		return c, nil
	}
	return nil, errors.New("Client not found")
}

// ClientWithID implements clients.Store
func (s *SimpleStorage) ClientWithID(id string) *clients.Client {
	if c, ok := s.clients[id]; ok {
		return &c
	}
	return nil
}

// SaveAuthorize saves authorize data.
func (s *SimpleStorage) SaveAuthorize(data *osin.AuthorizeData) error {
	if s.authorize.ItemCount() >= MaxCacheEntries {
		return errors.New("Maximum number of Authorize tokens reached")
	}
	s.authorize.Set(data.Code, data, cache.DefaultExpiration)
	return nil
}

// LoadAuthorize looks up AuthorizeData by a code.
// Client information MUST be loaded together.
// Optionally can return error if expired.
func (s *SimpleStorage) LoadAuthorize(code string) (*osin.AuthorizeData, error) {
	if d, ok := s.authorize.Get(code); ok {
		return d.(*osin.AuthorizeData), nil
	}
	return nil, errors.New("Authorize not found")
}

// RemoveAuthorize revokes or deletes the authorization code.
func (s *SimpleStorage) RemoveAuthorize(code string) error {
	s.authorize.Delete(code)
	return nil
}

// SaveAccess writes AccessData.
// If RefreshToken is not blank, it must save in a way that can be loaded using LoadRefresh.
func (s *SimpleStorage) SaveAccess(data *osin.AccessData) error {
	if s.access.ItemCount() >= MaxCacheEntries {
		return errors.New("Maximum number of Access tokens reached")
	}
	cacheduration := data.ExpireAt().Sub(time.Now())
	s.access.Set(data.AccessToken, data, cacheduration)
	if data.RefreshToken != "" {
		s.refresh.Set(data.RefreshToken, data.AccessToken, cacheduration)
	}
	return nil
}

// LoadAccess retrieves access data by token. Client information MUST be loaded together.
// AuthorizeData and AccessData DON'T NEED to be loaded if not easily available.
// Returns error if expired.
func (s *SimpleStorage) LoadAccess(code string) (*osin.AccessData, error) {
	if d, ok := s.access.Get(code); ok {
		data := d.(*osin.AccessData)
		if !data.IsExpired() {
			return data, nil
		}
		s.RemoveAccess(code)
	}
	return nil, errors.New("Access not found")
}

// RemoveAccess revokes or deletes an AccessData.
func (s *SimpleStorage) RemoveAccess(code string) error {
	s.access.Delete(code)
	return nil
}

// LoadRefresh retrieves refresh AccessData. Client information MUST be loaded together.
// AuthorizeData and AccessData DON'T NEED to be loaded if not easily available.
// Optionally can return error if expired.
func (s *SimpleStorage) LoadRefresh(code string) (*osin.AccessData, error) {
	if d, ok := s.refresh.Get(code); ok {
		return s.LoadAccess(d.(string))
	}
	return nil, errors.New("Refresh not found")
}

// RemoveRefresh revokes or deletes refresh AccessData.
func (s *SimpleStorage) RemoveRefresh(code string) error {
	s.refresh.Delete(code)
	return nil
}
