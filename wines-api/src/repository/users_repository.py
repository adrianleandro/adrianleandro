from fastapi import HTTPException

import uuid
import logging

from src.repository.base import BaseRepository, Session

from src.models.wine import Wine
from src.models.user import User
from src.models.preference import Preference
from src.models.rating import Rating
from src.repository.table_models import User as UserModel, FavoriteWines, Wine as WineModel, WineRating as WineRatingModel, PreferenceOption as PreferenceModel, UserPreference as UserPreferenceModel
from src.repository.preferences_repository import PreferencesRepository
from src.repository.ratings_repository import WineRatingsRepository

class UsersRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_user_by_id(self, user_uid: str) -> User:
        try:
            uuid.UUID(user_uid)
        except ValueError:
            logging.error(f'El id {user_uid} no es un UUID valido')
            raise KeyError('Formato de ID de usuario invalido')

        user_row = self.session.query(UserModel).filter(UserModel.uid == user_uid).first()
        if not user_row:
            raise KeyError('El usuario no existe')
        user = User(uid=user_row.uid, username=user_row.name, email=user_row.email)
        user.onboarding_completed = user_row.onboarding_completed
        try:
            user.add_preferences(PreferencesRepository(self.session).get_preferences(user.uid))
        except Exception as e:
            if "no tiene preferencias registradas" in str(e):
                # Inicializar con lista vacía
                user.preferences = []
            else:
                # Para otros errores, reenviar la excepción
                raise e
        user.set_favorites(self.get_favorite_wines(user))
        user.set_ratings(WineRatingsRepository(self.session).get_by_user_id(user_id=user.uid_to_str()))
        return user

    def get_favorite_wines(self, user: User):
        favorites = self.session.query(WineModel).join(FavoriteWines, WineModel.wine_id == FavoriteWines.wine_id).filter(FavoriteWines.user_id == user.uid_to_str()).order_by(FavoriteWines.added_date.desc()).all()
        wines = []
        for wine in favorites:
            wines.append(Wine(wine.wine_id, wine.wine_name, wine.type, wine.elaborate, wine.abv, wine.body, wine.country, wine.region, wine.winery, wine.summary))
        return wines

    def get_preferences(self, user: User):
        saved_preferences = self.session.query(PreferenceModel).join(UserPreferenceModel, PreferenceModel.id == UserPreferenceModel.option_id).filter(UserPreferenceModel.user_id == user.uid_to_str()).order_by(UserPreferenceModel.id.desc()).all()
        preferences = []
        for pref in saved_preferences:
            preferences.append(Preference(pref.id, pref.option, pref.description, pref.value))
        return preferences

    def save(self, user: User):
        logging.info(f'Saving user with ID {user.uid_to_str()}')

        existing_user = self.session.get(UserModel, user.uid_to_str())

        if existing_user:
            existing_user.name = user.username
            existing_user.email = user.email
        else:
            new_user = UserModel(uid=user.uid, name=user.username, email=user.email)
            self.session.add(new_user)

        preferences = [preference.id for preference in self.get_preferences(user)]
        for preference in user.preferences:
            preference_id = preference if isinstance(preference, int) else preference.id
            if preference_id not in preferences:
                logging.info(f'New preference detected: {preference_id} saving...')
                self.session.add(UserPreferenceModel(user_id=user.uid_to_str(), option_id=preference_id))
                if existing_user:
                    existing_user.onboarding_completed = True
                    self.session.add(existing_user)

        favorites = [favorite.id for favorite in self.get_favorite_wines(user)]
        for favorite in user.get_favorites():
            if favorite.id not in favorites:
                logging.info(f'New favorite detected: {favorite.wine_id} saving...')
                self.session.add(FavoriteWines(user_id=user.uid_to_str(), wine_id=favorite.wine_id))

        self.session.commit()
        return user

    def delete_favorite_wine(self, user: User, wine_id):
        favorite_ids = [fav.id for fav in user.get_favorites()]
        if wine_id not in favorite_ids:
            raise ValueError('Wine not in favorites')

        self.session.query(FavoriteWines).filter(FavoriteWines.user_id == user.uid_to_str(), FavoriteWines.wine_id == wine_id).delete()
        self.session.commit()