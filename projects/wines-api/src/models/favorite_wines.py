import uuid

class Rating:
    user_id: uuid.UUID
    wine_id: int
    rating: float

    def __init__(self, user_id, wine_id, rating):
        self.user_id = user_id
        self.wine_id = wine_id

        if rating < 0 or rating > 5:
            raise ValueError("Rating score must be between 0 and 5")
        self.rating = rating