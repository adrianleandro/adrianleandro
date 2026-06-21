import logging
import uuid

from sqlalchemy import select

from src.repository.base import BaseRepository, Session
from src.models.rating import Rating
from src.models.wine import Wine
from src.repository.table_models.wine_ratings import WineRating as WineRatingModel
from src.repository.table_models.wines import Wine as WineModel

class WineRatingsRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_user_id_and_wine_id(self, user_id: str, wine_id: int):
        return self.session.execute(
            select(WineModel, WineRatingModel)
            .join(WineRatingModel, WineModel.wine_id == WineRatingModel.wine_id)
            .where(
                WineRatingModel.user_id == user_id,
                WineRatingModel.wine_id == wine_id
            )
        ).first()

    def get_by_user_id(self, user_id: str):
        results = self.session.execute(
            select(WineModel, WineRatingModel)
            .join(WineRatingModel, WineModel.wine_id == WineRatingModel.wine_id)
            .where(WineRatingModel.user_id == user_id)
            .order_by(WineRatingModel.date.desc())
        ).all()
        ratings = []
        for wine, rating in results:
            rated_wine = Wine(wine.wine_id, wine.wine_name, wine.type, wine.elaborate, wine.abv, wine.body, wine.country, wine.region, wine.winery, wine.summary)
            ratings.append(Rating(user_id, rated_wine, rating.rating, rating.review))
        return ratings

    def get_by_wine_id(self, wine_id: str):
        results = self.session.execute(
            select(WineModel, WineRatingModel)
            .join(WineRatingModel, WineModel.wine_id == WineRatingModel.wine_id)
            .where(WineRatingModel.wine_id == wine_id)
            .order_by(WineRatingModel.date.desc())
        ).all()
        ratings = []
        for wine, rating in results:
            rated_wine = Wine(wine.wine_id, wine.wine_name, wine.type, wine.elaborate, wine.abv, wine.body, wine.country, wine.region, wine.winery, wine.summary)
            ratings.append(Rating(rating.user_id, rated_wine, rating.rating, rating.review))
        return ratings

    def save(self, rating: Rating):
        try:
            result = self.get_by_user_id_and_wine_id(str(rating.user_id), rating.wine.wine_id)
            if result:
                wine, original_rating = result
                original_rating.rating = rating.rating
                original_rating.review = rating.review
            else:
                self.session.add(WineRatingModel(
                    user_id=str(rating.user_id),
                    wine_id=rating.wine.wine_id,
                    rating=rating.rating,
                    review=rating.review
                ))

            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            logging.error(f'Error saving rating: {e}')
            return False