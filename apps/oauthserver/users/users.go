package users

import "errors"

//UserDetails is the profile information
type UserDetails struct {
	Login  string
	Name   string
	Email  []string
	Scopes []string
}

var (
	UserNotFoundError        = errors.New("User not found")
	InvalidPasswordError     = errors.New("Invalid password")
	InvalidSecurityCodeError = errors.New("Invalid security code")
)

//UserStore defines the interface for user information
type UserStore interface {
	//Get user details
	Get(username string) (*UserDetails, error)

	//Validate checks if a given password is correct for a username and returns the available scopes
	//
	// If the user credientials could not be validated, it returns one of the
	// following errors: UserNotFoundError, InvalidPasswordError,
	// InvalidSecurityCodeError or a custom error
	Validate(username, password, securityCode string) (scopes []string, err error)

	//Close frees resources like connectionpools for example
	Close()
}
