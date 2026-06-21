import copy 
from services.shared import base, create_simple

def create(
    inbox_domain,
    inbox_amount,
    outbox_domain,
    outbox_amount,
    comparer,
    index,
    value,
):
    services = create_simple(
        inbox_domain,
        inbox_amount,
        outbox_domain,
        outbox_amount,
    )

    for item in services.values():
        item["image"] = "year:latest"
        item["environment"]["COMPARATOR"] = comparer
        item["environment"]["INDEX"] = index
        item["environment"]["VALUE"] = value
    return services