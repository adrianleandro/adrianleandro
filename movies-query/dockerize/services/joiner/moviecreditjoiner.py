import services.joiner.joiner as joiner

def create(
    inbox_amount,
    outbox_amount,
    dispatcher_amount,
):
    return joiner.create(
        inbox_domain="moviecreditjoiner",
        inbox_amount=inbox_amount,
        outbox_domain="top_appearances",
        outbox_amount=outbox_amount,
        left_index=0,
        right_index=0,
        dispatcher_domain="creditdispatcher",
        dispatcher_amount=dispatcher_amount,
    )