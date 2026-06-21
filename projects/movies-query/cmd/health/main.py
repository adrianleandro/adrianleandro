import logging
import os
import yaml
from configparser import ConfigParser
from signal import signal, SIGTERM

from src.health import HealthChecker

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
    config.read("/app/health_checker_config.ini")

    config_params = {}
    try:
        config_params["id"] = int(os.environ.get('ID', None))
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
        config_params["compose_file"] = os.getenv('COMPOSE_FILE', config["DEFAULT"]["COMPOSE_FILE"])
    except KeyError as e:
        raise KeyError("Key was not found. Error: {}. Aborting health checker".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting health checker".format(e))

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

def load_compose(path):
    with open(path, "r") as file:
        return yaml.safe_load(file)

def main():
    try:
        config_params = initialize_config()
        logging_level = config_params["logging_level"]
        compose_file = config_params["compose_file"]
        identifier = config_params["id"]

        initialize_log(logging_level)

        if identifier is None:
            logging.critical(f"action: startup | result: fail | info: ID is not defined")
            # Exit with error code
            import sys
            sys.exit(1)

        compose = load_compose(compose_file)
        compose_services = compose.get("services", {}).keys()
        services = list(filter(
            lambda x: x != "mom" and not x.startswith("client") and x != "sentimentanalyzer",
            compose_services
        ))

        logging.debug(f"action: config | result: success | logging_level: {logging_level} | services: {', '.join(services)}")

        checker = HealthChecker(identifier, services)

        def handle_sigterm(signum, frame):
            logging.info("action: shutdown | result: in_progress | info: received SIGTERM")
            checker.signal_exit(signum, frame)

        signal(SIGTERM, handle_sigterm)

        logging.info("action: startup | result: success | info: health checker starting")
        checker.start()
    except Exception as e:
        logging.critical(f"action: startup | result: error | error: {e}")
        # Exit with error code
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()