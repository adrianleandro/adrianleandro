import services.filters.year.year as year

def create(inbox_amount, outbox_amount):
    return year.create(
        inbox_domain="filter_by_year_after_2000",
        inbox_amount=inbox_amount,
        outbox_domain="yearselector",
        outbox_amount=outbox_amount,
        comparer="GREATER",
        index=4,
        value="1999-12-31",
    )