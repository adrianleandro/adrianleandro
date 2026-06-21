import services.userdispatcher.userdispatcher as userdispatcher

def create(
    inbox_amount,
    outbox_amount,
):
    return userdispatcher.create(
        prefix="rating",
        inbox_amount=inbox_amount,
        outbox_domain="movieratingsharder",
        outbox_amount=outbox_amount,
    )