package serialization

import (
	"encoding/json"
	"io"
	"os"

	"fmt"

	"github.com/distribuidos-unrust/tp/configs"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/state"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

func StateFilename(parentDir string, inbox string, id uint32) string {
	return parentDir + "/" + inbox + "_" + fmt.Sprint(id) + ".json"
}

func StateFromFile(service *service.Service) (*state.State, error) {
	err := os.MkdirAll(configs.StatePath, configs.PermissionMode)
	if err != nil {
		return nil, err
	}

	filename := StateFilename(configs.StatePath, service.Name.String(), uint32(service.ID))
	log.Debugf(
		"action: state_from_file | result: success | filename: %s | service_name: %s | ID: %d",
		filename,
		service.Name.String(),
		uint32(service.ID),
	)

	jsonFile, err := os.OpenFile(filename, os.O_RDWR|os.O_CREATE, configs.PermissionMode)
	if err != nil {
		return nil, err
	}
	defer jsonFile.Close()

	bytes, err := io.ReadAll(jsonFile)
	if err != nil {
		return nil, err
	}

	if len(bytes) == 0 {
		state := state.NewState(service)
		return state, nil
	}

	var state state.State
	err = json.Unmarshal(bytes, &state)
	if err != nil {
		return nil, err
	}

	log.Debugf(
		"action: state_from_file | result: success | service_name: %s | ID: %d | counter: %d | seen_messages: %d",
		state.Service.Name.String(),
		uint32(state.Service.ID),
		state.Counter,
		len(state.MessageSeen),
	)
	return &state, nil
}

func StateIntoFile(state *state.State) error {
	filename := StateFilename(configs.StatePath, state.Service.Name.String(), uint32(state.Service.ID))
	jsonFile, err := os.OpenFile(filename, os.O_RDWR|os.O_CREATE|os.O_TRUNC, configs.PermissionMode)
	if err != nil {
		return err
	}
	defer jsonFile.Close()

	bytes, err := json.Marshal(state)
	if err != nil {
		return err
	}

	_, err = jsonFile.Write(bytes)
	if err != nil {
		return err
	}
	return nil
}
