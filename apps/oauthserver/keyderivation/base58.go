//
//Library for bitcoin base58 encoding decoding based on the bitcoin base58 implementation:
//https://github.com/bitcoin/bitcoin/blob/master/src/base58.cpp
//

package keyderivation

import (
	"math/big"
	"strings"
)

const pszBase58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

//DecodeBase58 decodes a base58-encoded string (psz).
func DecodeBase58(psz string) (result []byte) {
	//Strip leading and trailing spaces
	psz = strings.TrimSpace(psz)

	//Count leading '1's.
	zeroes := 0
	for _, pszchar := range psz {
		if pszchar != '1' {
			break
		}
		zeroes++
	}
	radix := big.NewInt(58)
	b256 := new(big.Int)
	//Process the characters.
	for _, pszchar := range psz[zeroes:] {
		//Decode base58 character
		charvalue := strings.IndexRune(pszBase58, pszchar)
		if charvalue == -1 {
			return nil
		}
		//Apply "b256 = b256 * 58 + charvalue".
		b256.Mul(b256, radix)
		b256.Add(b256, big.NewInt(int64(charvalue)))
	}

	// //Add leading zeroes
	encoded := b256.Bytes()
	result = make([]byte, zeroes+len(encoded))
	copy(result[zeroes:], encoded)

	return
}

//EncodeBase58 encodes a byte slice a base58-encoded string
func EncodeBase58(binarray []byte) string {
	base256 := new(big.Int)
	base256.SetBytes(binarray)
	radix := big.NewInt(58)

	encoded := make([]byte, 0, len(binarray)*136/100)

	mod := new(big.Int)
	zero := big.NewInt(0)

	//Build up base58 in reverse order
	for base256.Cmp(zero) > 0 {
		base256.DivMod(base256, radix, mod)
		encoded = append(encoded, pszBase58[mod.Int64()])
	}

	//Add leading zeroes
	zerochar := pszBase58[0]
	for _, value := range binarray {
		if value != 0 {
			break
		}
		encoded = append(encoded, zerochar)
	}

	//Reverse
	encodedLength := len(encoded)
	for i := 0; i < encodedLength/2; i++ {
		encoded[i], encoded[encodedLength-1-i] = encoded[encodedLength-1-i], encoded[i]
	}

	return string(encoded)
}
