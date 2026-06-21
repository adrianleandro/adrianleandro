import services.selector.selector as selector


def create(
    inbox_amount,
    containscountry_ar,
    onlyoneprodcountry,
    rentability,
):
    return selector.create(
        inbox_domain="moviesselector",
        inbox_amount=inbox_amount,
        outboxes=[
            {
                "domain": "containscountry_ar",
                "indexes": "[5, 20, 3, 13, 14]",
                "amount": containscountry_ar,
            },
            {
                "domain": "onlyoneprodcountry",
                "indexes": "[5, 13, 2]",
                "amount": onlyoneprodcountry,
            },
            {
                "domain": "rentability",
                "indexes": "[5, 15, 2, 9]",
                "amount": rentability,
            },
        ],
    )
