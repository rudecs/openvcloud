package tfa

const NumRecoveryCodes = 10

type Recovery struct {
	Codes []*RecoveryCode
}

type RecoveryCode struct {
	Code string `json:"code"`
	Used bool   `json:"used"`
}

func (r *Recovery) GenerateCodes() {
	r.Codes = make([]*RecoveryCode, NumRecoveryCodes)
	for i, _ := range r.Codes {
		r.Codes[i] = NewRecoveryCode()
	}
}

func NewRecoveryCode() *RecoveryCode {
	return &RecoveryCode{
		Code: generateRandomString([]rune("0123456789"), 6),
	}
}
