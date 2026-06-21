import copy

NETWORK = "tp_net"
CONFIGS_VOLUME = "./configs/configs.yml:/app/configs/configs.yml"
STATES_VOLUME = "./state:/app/state"

base = {
    "depends_on": {"mom": {"condition": "service_healthy"}},
    "entrypoint": "./main",
    "image": "containscountry:latest",
    "networks": [NETWORK],
    "volumes": [CONFIGS_VOLUME, STATES_VOLUME],
}


def create(
    data,
    inbox_amount,
    output_amount,
):
    services = {}
    for i in range(inbox_amount):
        item = copy.deepcopy(base)
        item.update(copy.deepcopy(data))
        item["container_name"] = item["container_name"].format(ID=i)
        item["environment"]["ID"] = i
        item["environment"]["INBOX_AMOUNT"] = inbox_amount
        item["environment"]["OUTBOX_AMOUNT"] = output_amount
        services[item["container_name"]] = item
    return services


def create_with_inbox(inbox_domain, inbox_amount):
    services = {}
    for i in range(inbox_amount):
        item = copy.deepcopy(base)
        item["container_name"] = f"{inbox_domain}_{i}"
        item["environment"] = {}
        item["environment"]["ID"] = i
        item["environment"]["INBOX_DOMAIN"] = inbox_domain
        item["environment"]["INBOX_AMOUNT"] = inbox_amount
        services[item["container_name"]] = item
    return services


def create_simple(
    inbox_domain,
    inbox_amount,
    outbox_domain,
    outbox_amount,
):
    services = create_with_inbox(inbox_domain, inbox_amount)
    for item in services.values():
        item["environment"]["OUTBOX_DOMAIN"] = outbox_domain
        item["environment"]["OUTBOX_AMOUNT"] = outbox_amount
    return services


def create_multiple_outbox(
    data,
    inbox_amount,
    outboxes,
):
    services = {}
    for i in range(inbox_amount):
        item = copy.deepcopy(base)
        item.update(copy.deepcopy(data))
        item["container_name"] = item["container_name"].format(ID=i)
        item["environment"]["ID"] = i
        item["environment"]["INBOX_AMOUNT"] = inbox_amount

        for j, outbox_amount in enumerate(outboxes):
            item["environment"][f"OUTBOX_{j}_AMOUNT"] = outbox_amount

        services[item["container_name"]] = item

    return services
