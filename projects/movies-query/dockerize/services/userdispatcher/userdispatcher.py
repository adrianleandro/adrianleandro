from services.shared import create_simple


def create(prefix, inbox_amount, outbox_domain, outbox_amount):
    services = create_simple(
        inbox_domain=f"{prefix}dispatcher",
        inbox_amount=inbox_amount,
        outbox_domain=outbox_domain,
        outbox_amount=outbox_amount,
    )
    for item in services.values():
        item["image"] = "userdispatcher:latest"
        item["environment"]["PREFIX"] = f"{prefix}splitted"
    return services