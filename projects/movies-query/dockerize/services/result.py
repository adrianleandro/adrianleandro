from services.shared import base
import copy

data = {
    "container_name": "resultq{Q}_{ID}",
    "image": "result:latest",
    "environment": {
        "ID": 0,
        "QUERY": 0,
        "INBOX_DOMAIN": "resultq{Q}",
        "INBOX_AMOUNT": 0,
    },
}


def create(query, inbox_amount):
    services = {}
    for id in range(inbox_amount):
        item = copy.deepcopy(base)
        item.update(copy.deepcopy(data))
        item["container_name"] = item["container_name"].format(Q=query, ID=id)
        item["environment"]["ID"] = id
        item["environment"]["QUERY"] = query
        item["environment"]["INBOX_AMOUNT"] = inbox_amount
        item["environment"]["INBOX_DOMAIN"] = item["environment"][
            "INBOX_DOMAIN"
        ].format(Q=query)
        services[item["container_name"]] = item
    return services
