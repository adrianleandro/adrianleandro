import services.counter.counter as counter

def create(inbox_amount, outbox_amount):
    return counter.create(
        inbox_domain="top_rating",
        inbox_amount=inbox_amount,
        outbox_domain="resultq3",
        outbox_amount=outbox_amount,
        key_index=3,
        value_index=1,
        top=1,
        ascending=0,
        minmax=1,
        kind=2,
    )