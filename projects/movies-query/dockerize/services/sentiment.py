import services.shared as shared

def create(inbox_amount, outbox_amount):
    services = shared.create_simple(
        inbox_domain="sentiment",
        inbox_amount=inbox_amount,
        outbox_domain="average_ratio",
        outbox_amount=outbox_amount,
    )

    for item in services.values():
        item["image"] = "sentiment:latest"
        item["depends_on"]["sentimentanalyzer"] = {"condition": "service_started"}
    return services
