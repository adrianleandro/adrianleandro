import services.usersplitter.usersplitter as usersplitter

def create(
    inbox_amount,
):
    return usersplitter.create(
        prefix="rating",
        inbox_amount=inbox_amount,
    )