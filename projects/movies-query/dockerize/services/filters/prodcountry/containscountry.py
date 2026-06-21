import copy
import services.shared as shared

def create(
    inbox_domain,
    inbox_amount,
    outbox_domain,
    outbox_amount,
    country,
    index,
):
    services = shared.create_simple(
        inbox_domain,
        inbox_amount,
        outbox_domain,
        outbox_amount,
    )
    for service in services.values():
        service["image"] = "containscountry:latest"
        service["environment"]["COUNTRY"] = country
        service["environment"]["INDEX"] = index
    return services

