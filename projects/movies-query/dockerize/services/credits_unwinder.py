data = {
    "container_name": "credits_unwinder_{ID}",
    "image": "unwindcredits:latest",
    "environment": {
        "ID": 0,
        "CAST_INDEX": 0,
        "MOVIE_INDEX": 2,
        "INBOX_DOMAIN": "credits_unwinder",
        "INBOX_AMOUNT": 0,
        "OUTBOX_DOMAIN": "creditsplitter",
        "OUTBOX_AMOUNT": 0,
    },
}