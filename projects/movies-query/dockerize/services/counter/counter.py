import copy
from services.shared import base, create_simple

def create(
    inbox_domain,
    inbox_amount,
    outbox_domain,
    outbox_amount,
    key_index,
    value_index,
    top,
    ascending,
    minmax,
    kind,
):
    services = create_simple(
        inbox_domain=inbox_domain,
        inbox_amount=inbox_amount,
        outbox_domain=outbox_domain,
        outbox_amount=outbox_amount,
    )
    for item in services.values():
        item["image"] = "counter:latest"
        item["environment"]["KEYINDEX"] = key_index
        item["environment"]["VALUEINDEX"] = value_index
        item["environment"]["TOP"] = top
        item["environment"]["ASCENDING"] = ascending
        item["environment"]["MINMAX"] = minmax
        item["environment"]["KIND"] = kind
    return services
