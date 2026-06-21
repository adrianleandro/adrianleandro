import services.counter.counter as counter

def create(inbox_amount, outbox_amount):
    return counter.create(
        inbox_domain="top_appearances",
        inbox_amount=inbox_amount,
        outbox_domain="resultq4",
        outbox_amount=outbox_amount,
        key_index=1,
        value_index=2,
        top=10,
        ascending=0,
        minmax=0,
        kind=1,
    )