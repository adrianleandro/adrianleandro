import services.filters.year.year as year

def create(inbox_amount, outbox_amount):
    return year.create(
        inbox_domain="filter_by_year_before_2010",
        inbox_amount=inbox_amount,
        outbox_domain="containscountry_es",
        outbox_amount=outbox_amount,
        comparer="LESSER",
        index=4,
        value="2011-01-01",
    )