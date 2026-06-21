from typing import Dict, List, Optional, Union
from pydantic import BaseModel
from src.models.schemas.base import BaseSchemaModel

class PreferenceAttributes(BaseSchemaModel):
    """Atributos agrupados para el modelo ML"""
    types: Dict[int, float]
    bodies: Dict[int, float]
    intensities: Dict[int, float]
    dryness: Dict[int, float]
    abv: Dict[int, float]

class PreferenceItem(BaseModel):
    """Un item de preferencia individual"""
    id: int
    option: str
    description: Optional[str] = None
    value: float
    weight: float = 1.0
    category: dict

class OnboardingPreferences(BaseModel):
    """Preferencias seleccionadas durante el onboarding"""
    option_ids: List[int]
    weights: Optional[Dict[int, float]] = None

class CategoryPreferences(BaseModel):
    """Preferencias para una categoría específica"""
    option_ids: List[int]
    weights: Optional[Dict[int, float]] = None

class UserPreferencesResponse(BaseModel):
    """Respuesta con las preferencias del usuario en formato agrupado"""
    user_id: str
    preferences: PreferenceAttributes

class UserPreferencesListResponse(BaseModel):
    """Respuesta con lista de preferencias del usuario"""
    user_id: str
    preferences: List[PreferenceItem]