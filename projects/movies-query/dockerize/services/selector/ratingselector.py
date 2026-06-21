import services.selector.selector as selector


def create(
    inbox_amount,
    ratingsplitter,
):
    return selector.create(
        inbox_domain="ratingselector",
        inbox_amount=inbox_amount,
        outboxes=[
            {
                "domain": "ratingsplitter",
                "indexes": "[1, 2]",
                "amount": ratingsplitter,
            }
        ],
    )
