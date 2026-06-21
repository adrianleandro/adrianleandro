#!/usr/bin/env python3

import socket
import logging
import os
from configparser import ConfigParser
from common.server import Server
from signal import signal, SIGTERM

def initialize_config():
    """ Parse env variables or config file to find program config params

    Function that search and parse program configuration parameters in the
    program environment variables first and the in a config file.
    If at least one of the config parameters is not found a KeyError exception
    is thrown. If a parameter could not be parsed, a ValueError is thrown.
    If parsing succeeded, the function returns a ConfigParser object
    with config parameters
    """

    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("/app/config.ini")

    config_params = {}
    try:
        config_params["port"] = int(os.getenv('SERVER_PORT', config["DEFAULT"]["SERVER_PORT"]))
        config_params["listen_backlog"] = int(os.getenv('SERVER_LISTEN_BACKLOG', config["DEFAULT"]["SERVER_LISTEN_BACKLOG"]))
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
        # Add max_workers parameter with default value
        config_params["max_workers"] = int(os.getenv('SERVER_MAX_WORKERS', 
                                                    config["DEFAULT"].get("SERVER_MAX_WORKERS", "10")))
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params

def initialize_log(logging_level):
    """
    Python custom logging initialization

    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

def main():
    try:
        config_params = initialize_config()
        logging_level = config_params["logging_level"]
        port = config_params["port"]
        listen_backlog = config_params["listen_backlog"]
        max_workers = config_params["max_workers"]

        initialize_log(logging_level)

        logging.debug(f"action: config | result: success | port: {port} | "
                    f"listen_backlog: {listen_backlog} | logging_level: {logging_level} | "
                    f"max_workers: {max_workers}")

        server = Server(port, listen_backlog, max_workers)

        # Set up signal handler for graceful shutdown
        def handle_sigterm(signum, frame):
            logging.info("action: shutdown | result: in_progress | info: received SIGTERM")
            server.signal_exit(signum, frame)

        signal(SIGTERM, handle_sigterm)

        logging.info("action: startup | result: success | info: server starting")
        server.run()
    except Exception as e:
        logging.critical(f"action: startup | result: error | error: {e}")
        # Exit with error code
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
