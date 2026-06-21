package utils

import (
	"fmt"

	"github.com/distribuidos-unrust/tp/configs"
	"github.com/spf13/viper"
)

func InitViperConfig() (*viper.Viper, error) {
	v := viper.New()
	v.AutomaticEnv()
	v.SetConfigFile(configs.ConfigFilePath)
	if err := v.ReadInConfig(); err != nil {
		fmt.Printf("Configuration could not be read from config file. Using env variables instead")
	}
	return v, nil
}
