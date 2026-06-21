import services.counter.counter as counter

def create(inbox_amount, outbox_amount):
    return counter.create(
        inbox_domain="average_ratio",
        inbox_amount=inbox_amount,
        outbox_domain="resultq5",
        outbox_amount=outbox_amount,
        key_index=5,
        value_index=4,
        top=0,
        ascending=0,
        minmax=0,
        kind=2,
    )