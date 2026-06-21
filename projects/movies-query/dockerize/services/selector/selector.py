import copy 
from services.shared import base

data = {
    "container_name": "{inbox_domain}_{ID}",
    "image": "selector:latest",
    "environment": {
        "ID": 0,
        "INBOX_DOMAIN": "{inbox_domain}",
        "INBOX_AMOUNT": 0,
    },
}

def create(
    inbox_domain,
    inbox_amount,
    outboxes
):
    services = {}
    for i in range(inbox_amount):
        item = copy.deepcopy(base)
        item.update(copy.deepcopy(data))
        item["container_name"] = item["container_name"].format(
            inbox_domain=inbox_domain, ID=i
        )
        item["environment"]["ID"] = i
        item["environment"]["INBOX_DOMAIN"] = inbox_domain
        item["environment"]["INBOX_AMOUNT"] = inbox_amount

        item["environment"]["OUTBOXES_AMOUNT"] = len(outboxes)
        
        for j, outbox in enumerate(outboxes):
            item["environment"][f"OUTBOX_{j}_DOMAIN"] = outbox["domain"]
            item["environment"][f"OUTBOX_{j}_INDEXES"] = outbox["indexes"]
            item["environment"][f"OUTBOX_{j}_AMOUNT"] = outbox["amount"]

        services[item["container_name"]] = item
    return services