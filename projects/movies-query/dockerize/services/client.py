import copy
from services.shared import NETWORK, CONFIGS_VOLUME

client = {
    "container_name": "client_{ID}",
    "depends_on": [],
    "image": "client:latest",
    "networks": [NETWORK],
    "volumes": [
        CONFIGS_VOLUME,
        "./data:/app/data"
    ],
    "environment": {
        "RESULTS_AMOUNT": 5,
        "OUTBOX_DOMAIN": "gateway",
        "OUTBOX_AMOUNT": 1
    }
}

def create(client_amount, gateway_amount):
    clients = {}
    for i in range(client_amount):
        item = copy.deepcopy(client)
        item["container_name"] = item["container_name"].format(ID=i)
        item["environment"]["ID"] = i
        item["environment"]["OUTBOX_AMOUNT"] = gateway_amount
        item["depends_on"] = [f"gateway_{j}" for j in range(gateway_amount)]
        clients[item["container_name"]] = item
    return clients
    