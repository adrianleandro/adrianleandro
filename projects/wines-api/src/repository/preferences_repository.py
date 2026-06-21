import logging

from sqlalchemy import select, delete

from src.repository.base import BaseRepository, Session
from src.models.preference import Preference
from src.models.preference_category import PreferenceCategory
from src.repository.table_models.preference_options import PreferenceOption as PreferenceOptionModel
from src.repository.table_models.preference_categories import PreferenceCategory as PreferenceCategoryModel
from src.repository.table_models.user_preferences import UserPreference as UserPreferenceModel

class PreferencesRepository(BaseRepository):
    def __init__(self, session: Session):
        super().__init__(session)

    def get_options(self):
        query = select(PreferenceCategoryModel, PreferenceOptionModel).join(
            PreferenceOptionModel,
            PreferenceCategoryModel.id == PreferenceOptionModel.category_id
        )

        results = []
        for category, option in self.session.execute(query):
            preference = Preference(option.id, option.option, option.description, option.value)
            preference.set_category(category)
            results.append(preference)
        return results

    def get_preferences(self, user_id):
        """Obtiene las preferencias de un usuario"""
        # El error está ocurriendo aquí - este método debe devolver una lista vacía
        # en lugar de lanzar una excepción cuando no hay preferencias
        
        try:
            preferences = (self.session.query(
                UserPreferenceModel,
                PreferenceOptionModel,
                PreferenceCategoryModel,
            ).join(
                PreferenceOptionModel,
                UserPreferenceModel.option_id == PreferenceOptionModel.id
            )
            .join(
                PreferenceCategoryModel,
                PreferenceCategoryModel.id == PreferenceOptionModel.category_id,
            )
            .filter(
                UserPreferenceModel.user_id == user_id
            ).all())
            user_preferences = []
            for (user_pref, option, category) in preferences:
                pref = Preference(
                    option.id,
                    option.option,
                    option.description,
                    option.value
                )
                pref.set_category(PreferenceCategory(category.id, category.name, category.description))
                user_preferences.append(pref)
            
            # Si no hay preferencias, devolver una lista vacía en lugar de error
            if not user_preferences:
                return []
                
            return user_preferences
            
        except Exception as e:
            print(f"Error al obtener preferencias: {str(e)}")
            # Devolver lista vacía en caso de error
            return []
        
    def save_onboarding_preferences(self, user_id: str, preference_options: list[int], weights: dict = None):
        """
        Guarda todas las preferencias de un usuario durante el onboarding
        
        Args:
            user_id: UUID del usuario
            preference_options: Lista de IDs de opciones de preferencia
            weights: Diccionario opcional de {option_id: weight} para pesos personalizados
        """
        try:
            # Eliminar preferencias existentes para este usuario
            self.session.query(UserPreferenceModel).filter(
                UserPreferenceModel.user_id == user_id
            ).delete(synchronize_session=False)
            
            # Verificar que los option_ids existen
            valid_options = set(opt[0] for opt in self.session.query(PreferenceOptionModel.id).all())
            invalid_options = [opt_id for opt_id in preference_options if opt_id not in valid_options]
            
            if invalid_options:
                raise ValueError(f"Opciones de preferencia inválidas: {invalid_options}")
            
            # Agregar nuevas preferencias
            for option_id in preference_options:
                weight = weights.get(option_id, 1.0) if weights else 1.0
                user_pref = UserPreferenceModel(
                    user_id=user_id,
                    option_id=option_id,
                    weight=weight
                )
                self.session.add(user_pref)
            
            self.session.commit()
            return True
            
        except Exception as e:
            self.session.rollback()
            raise e
    
    def update_category_preferences(self, user_id: str, category_id: int, preference_options: list[int], weights: dict = None):
        """
        Actualiza las preferencias para una categoría específica
        
        Args:
            user_id: UUID del usuario
            category_id: ID de la categoría a actualizar
            preference_options: Lista de IDs de opciones de preferencia dentro de esa categoría
            weights: Diccionario opcional de {option_id: weight} para pesos personalizados
        """
        # Obtener todos los IDs de opciones para esta categoría
        category_options = self.session.query(PreferenceOptionModel.id).filter(
            PreferenceOptionModel.category_id == category_id
        ).all()
        category_option_ids = [option[0] for option in category_options]
        
        # Eliminar preferencias existentes para esta categoría
        self.session.query(UserPreferenceModel).filter(
            UserPreferenceModel.user_id == user_id,
            UserPreferenceModel.option_id.in_(category_option_ids)
        ).delete(synchronize_session=False)
        
        # Agregar nuevas preferencias
        for option_id in preference_options:
            # Verificar que la opción pertenezca a la categoría especificada
            if option_id in category_option_ids:
                weight = weights.get(option_id, 1.0) if weights else 1.0
                user_pref = UserPreferenceModel(
                    user_id=user_id,
                    option_id=option_id,
                    weight=weight
                )
                self.session.add(user_pref)
        
        self.session.commit()
        return True
    
    def get_user_preference_attributes(self, user_id: str) -> dict:
        """
        Obtiene las preferencias del usuario en formato agrupado por categorías para el modelo ML
        """
        # Inicializamos el diccionario resultado con valores vacíos
        result = {
            "types": {},
            "bodies": {},
            "intensities": {},
            "dryness": {},
            "abv": {}
        }
        
        try:
            # Obtener las preferencias del usuario
            preferences = self.get_preferences(user_id)
            
            # Si no hay preferencias, simplemente devolvemos el diccionario vacío
            if not preferences:
                return result
                
            # Mapeo de nombres de categorías
            category_name_map = {
                "types": "types",
                "bodies": "bodies", 
                "intensities": "intensities",
                "dryness": "dryness",
                "abv": "abv"
            }
            
            # Agrupamos las preferencias por categoría
            for pref in preferences:
                category_name = pref.category.name.lower()
                if category_name in category_name_map:
                    key = category_name_map[category_name]
                    result[key][pref.id] = float(pref.value)
                    
            return result
            
        except Exception as e:
            print(f"Error al obtener preferencias de usuario: {str(e)}")
            # En lugar de propagar el error, devolvemos el diccionario vacío
            return result