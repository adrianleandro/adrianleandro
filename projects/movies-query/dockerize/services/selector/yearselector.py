import services.selector.selector as selector


def create(
    inbox_amount,
    filter_by_year_before_2010_amount,
    movieratingsharder_amount,
    moviecreditsharder_amount,
):
    return selector.create(
        inbox_domain="yearselector",
        inbox_amount=inbox_amount,
        outboxes=[
            {
                "domain": "filter_by_year_before_2010",
                "indexes": "[0, 1, 2, 3, 4]",
                "amount": filter_by_year_before_2010_amount,
            },
            {
                "domain": "movieratingsharder",
                "indexes": "[0, 1]",
                "amount": movieratingsharder_amount,
            },
            {
                "domain": "moviecreditsharder",
                "indexes": "[0]",
                "amount": moviecreditsharder_amount,
            },
        ],
    )
