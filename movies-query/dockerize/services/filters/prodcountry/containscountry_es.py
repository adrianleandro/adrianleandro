import services.filters.prodcountry.containscountry as containscountry

def create(inbox_amount, outbox_amount):
    return containscountry.create(
        inbox_domain="containscountry_es",
        inbox_amount=inbox_amount,
        outbox_domain="resultq1",
        outbox_amount=outbox_amount,
        country="Spain",
        index=3,
    )