from services.shared import base
import copy

data = {
    "container_name": "{prefix}sharder_{ID}",
    "image": "sharder:latest",
    "environment": {
        "ID": 0,
        "INDEX": 0,
        "INBOX_DOMAIN": "{prefix}sharder",
        "INBOX_AMOUNT": 0,
        "OUTBOX_DOMAIN": "{output_domain}",
        "OUTBOX_AMOUNT": 0,
    },
}


def create(
    prefix: str, index: int, inbox_amount: int, outbox_amount, outbox_domain: str
) -> dict:
    services = {}
    for i in range(inbox_amount):
        item = copy.deepcopy(base)
        item.update(copy.deepcopy(data))
        item["container_name"] = item["container_name"].format(prefix=prefix, ID=i)
        item["environment"]["ID"] = i
        item["environment"]["INDEX"] = index
        item["environment"]["INBOX_DOMAIN"] = item["environment"][
            "INBOX_DOMAIN"
        ].format(prefix=prefix)
        item["environment"]["INBOX_AMOUNT"] = inbox_amount
        item["environment"]["OUTBOX_DOMAIN"] = outbox_domain
        item["environment"]["OUTBOX_AMOUNT"] = outbox_amount
        services[item["container_name"]] = item
    return services
