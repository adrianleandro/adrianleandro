import uuid
import logging
from src.models.rating import Rating
from src.models.wine import Wine

class User:
    uid: uuid.UUID
    username: str
    email: str
    onboarding_completed: bool
    preferences: list
    favorites: list
    ratings: list

    def __init__(self, uid: uuid.UUID, username: str, email: str):
        self.uid = uid
        self.username = username
        self.email = email
        self.preferences = []
        self.onboarding_completed = False

    def uid_to_str(self):
        return str(self.uid)

    def add_preferences(self, preferences):
        if not preferences:
            raise ValueError("El usuario no tiene preferencias registradas")
        self.preferences = preferences

    def _get_value_from_preference_category(self, selected_category: str):
        for preference in self.preferences:
            if preference.has_category(selected_category):
                return 1 if preference.value is None else preference.value
        return 1

    def favorite_type(self):
        types = {'Tinto': 'Red', 'Blanco': 'White', 'Rosado': 'Rose', 'Espumoso': 'Sparkling', 'No sabe/no contesta': 'Red'}
        for preference in self.preferences:
            if preference.has_category('types'):
                return types[preference.option]
        return None

    def favorite_body(self):
        return self._get_value_from_preference_category('bodies') * 100 % 6

    def favorite_dryness(self):
        return self._get_value_from_preference_category('dryness') * 100 % 6

    def favorite_abv(self):
        return self._get_value_from_preference_category('abv') or 0

    def rate_wine(self, wine, rating, review):
        return Rating(self.uid, wine, rating, review)

    def add_favorite(self, wine: Wine):
        self.favorites.append(wine)

    def set_favorites(self, favorites: list):
        self.favorites = favorites

    def get_favorites(self):
        return self.favorites

    def set_ratings(self, ratings: list):
        self.ratings = ratings

    def get_ratings(self, wine_id = None):
        if wine_id:
            for rating in self.ratings:
                if rating.wine.id == wine_id:
                    return rating
            return None
        return self.ratings