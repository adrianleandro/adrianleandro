import uuid
from src.models.wine import Wine

class Rating:
    user_id: uuid.UUID
    wine_id: int
    wine: Wine
    rating: float
    review: str

    def __init__(self, user_id, wine, rating, review):
        self.user_id = user_id
        self.wine_id = wine.id
        self.wine = wine
        self.review = review

        if rating and (rating < 0 or rating > 5):
            raise ValueError("Rating score must be between 0 and 5")
        self.rating = rating