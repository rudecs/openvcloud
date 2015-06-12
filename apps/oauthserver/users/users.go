package users

//UserDetails is the profile information
type UserDetails struct {
	Login string
	Name  string
	Email []string
}

//UserStore defines the interface for user information
type UserStore interface {
	//Get user details
	Get(username string) (*UserDetails, error)

	//Validate checks if a given password is correct for a username
	Validate(username, password string) bool

	//Close frees resources like connectionpools for example
	Close()
}
