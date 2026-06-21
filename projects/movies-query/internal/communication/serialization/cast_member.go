package serialization

import (
	"encoding/json"
	"strings"

	"github.com/distribuidos-unrust/tp/internal/models"
)

func CastMembersFromString(castMemberStr string) ([]models.CastMember, error) {
	castMemberStr = strings.Replace(castMemberStr, "\"", "|", -1)
	castMemberStr = strings.Replace(castMemberStr, "'", "\"", -1)
	castMemberStr = strings.Replace(castMemberStr, "|", "'", -1)
	castMemberStr = strings.Replace(castMemberStr, "None", "\"\"", -1)
	castMembers := make([]models.CastMember, 0)
	dat := []byte(castMemberStr)
	if err := json.Unmarshal(dat, &castMembers); err != nil {
		return nil, err
	}
	return castMembers, nil
}
