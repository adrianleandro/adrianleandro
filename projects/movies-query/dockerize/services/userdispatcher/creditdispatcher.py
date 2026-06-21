import services.userdispatcher.userdispatcher as userdispatcher

def create(
    inbox_amount,
    outbox_amount,
):
    return userdispatcher.create(
        prefix="credit",
        inbox_amount=inbox_amount,
        outbox_domain="moviecreditsharder",
        outbox_amount=outbox_amount,
    )