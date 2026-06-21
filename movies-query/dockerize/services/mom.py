mom = {
    "container_name": "mom",
    "build": {
        "context": "./deployment/rabbitmq/",
        "dockerfile": "Dockerfile"
    },
    "ports": ["15672:15672"],
    "networks": ["tp_net"],
    "healthcheck": {
        "test": "rabbitmq-diagnostics check_port_connectivity",
        "interval": "5s",
        "timeout": "20s",
        "retries": 5,
    },
}