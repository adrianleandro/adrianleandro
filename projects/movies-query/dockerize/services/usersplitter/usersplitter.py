from services.shared import create_with_inbox


def create(prefix, inbox_amount):
    services = create_with_inbox(
        inbox_domain=f"{prefix}splitter",
        inbox_amount=inbox_amount,
    )
    for item in services.values():
        item["image"] = "usersplitter:latest"
        item["environment"]["PREFIX"] = f"{prefix}splitted"
    return services