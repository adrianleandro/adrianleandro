import copy

data = {
    "container_name": "onlyoneprodcountry_{ID}",
    "image": "onlyoneprodcountry:latest",
    "environment": {
        "ID": 0,
        "INDEX": 1,
        "INBOX_DOMAIN" :"onlyoneprodcountry",
        "INBOX_AMOUNT": 0,
        "OUTBOX_DOMAIN": "top_ranking",
        "OUTBOX_AMOUNT": 0,
    },
}
