data = {
    "container_name": "rentability_{ID}",
    "image": "rentability:latest",
    "environment": {
        "ID": 0,
        "REVENUE_INDEX": 1,
        "BUDGET_INDEX": 2,
        "INBOX_DOMAIN": "rentability",
        "INBOX_AMOUNT": 0,
        "OUTBOX_DOMAIN": "sentiment",
        "OUTBOX_AMOUNT": 0,
    },
}