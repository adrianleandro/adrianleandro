import services.shared as shared

data = {
    "sentimentanalyzer": {
        "container_name": "sentimentanalyzer",
        "image": "analyzer:latest",
        "networks": [shared.NETWORK],
        "volumes": ["./configs/config.ini:/app/config.ini"],
    }
}

def create():
    return data

