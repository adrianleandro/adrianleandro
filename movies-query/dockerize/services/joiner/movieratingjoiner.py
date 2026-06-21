import services.joiner.joiner as joiner

def create(
    inbox_amount,
    outbox_amount,
    dispatcher_amount,
):
    return joiner.create(
        inbox_domain="movieratingjoiner",
        inbox_amount=inbox_amount,
        outbox_domain="top_rating",
        outbox_amount=outbox_amount,
        left_index=0,
        right_index=0,
        dispatcher_domain="ratingdispatcher",
        dispatcher_amount=dispatcher_amount,
    )