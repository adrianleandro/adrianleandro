import services.filters.prodcountry.containscountry as containscountry

def create(inbox_amount, outbox_amount):
    return containscountry.create(
        inbox_domain="containscountry_ar",
        inbox_amount=inbox_amount,
        outbox_domain="filter_by_year_after_2000",
        outbox_amount=outbox_amount,
        country="Argentina",
        index=3,
    )