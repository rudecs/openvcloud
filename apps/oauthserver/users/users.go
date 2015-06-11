package users

//UserStore defines the interface for user information
type UserStore interface {
	//Validate checks if a given password is correct for a username
	Validate(username, password string) bool

	//Close frees resources like connectionpools for example
	Close()
}
