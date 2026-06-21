from services.shared import create_simple

def create(
    inbox_domain: str,
    inbox_amount: int,
    outbox_domain: str,
    outbox_amount: int,
    left_index: int,
    right_index: int,
    dispatcher_domain: str,
    dispatcher_amount: int,
) -> dict:
    services = create_simple(
        inbox_domain=inbox_domain,
        inbox_amount=inbox_amount,
        outbox_domain=outbox_domain,
        outbox_amount=outbox_amount,
    )

    for item in services.values():
        item["image"] = "joiner:latest"
        item["environment"]["LEFT_INDEX"] = left_index
        item["environment"]["RIGHT_INDEX"] = right_index
        item["environment"]["DISPATCHER_DOMAIN"] = dispatcher_domain
        item["environment"]["DISPATCHER_AMOUNT"] = dispatcher_amount
    return services
