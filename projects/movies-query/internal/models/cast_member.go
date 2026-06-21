package models

type CastMember struct {
	CastID    int    `json:"cast_id"`
	Character string `json:"character"`
	CreditID  string `json:"credit_id"`
	Gender    int    `json:"gender"`
	ID        int    `json:"id"`
	Name      string `json:"name"`
	Order     int    `json:"order"`
}
