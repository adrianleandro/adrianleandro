import services.counter.counter as counter

def create(inbox_amount, outbox_amount):
    return counter.create(
        inbox_domain="top_ranking",
        inbox_amount=inbox_amount,
        outbox_domain="resultq2",
        outbox_amount=outbox_amount,
        key_index=1,
        value_index=2,
        top=5,
        ascending=0,
        minmax=0,
        kind=0,
    )