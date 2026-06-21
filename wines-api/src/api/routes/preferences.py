import fastapi
from fastapi import status, Depends, Path, HTTPException, Query
from typing import List

from src.api.dependencies import get_repository
from src.repository.preferences_repository import PreferencesRepository
from src.repository.users_repository import UsersRepository
from src.models.schemas.preference import OnboardingPreferences, CategoryPreferences, UserPreferencesResponse, PreferenceAttributes
from src.repository.table_models import User as UserModel

router = fastapi.APIRouter(prefix="/preferences", tags=["preferences"])

@router.get(
    "/options",
    summary="Get all preference options",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
)
async def get_preference_options(
    preferences_repo: PreferencesRepository = Depends(get_repository(repo_type=PreferencesRepository)),
):
    """Obtener todas las opciones de preferencias disponibles"""
    options = preferences_repo.get_options()
    return [
        {
            "id": option.id,
            "option": option.option,
            "description": option.description,
            "value": option.value,
            "category": {
                "id": option.category.id,
                "name": option.category.name,
                "description": option.category.description
            }
        } for option in options
    ]

@router.post(
    "/users/{user_id}/onboarding",
    summary="Save all user preferences during onboarding",
    status_code=status.HTTP_201_CREATED,
)
async def save_onboarding_preferences(
    preferences: OnboardingPreferences,
    user_id: str = Path(..., title="ID del usuario"),
    preferences_repo: PreferencesRepository = Depends(get_repository(repo_type=PreferencesRepository)),
    users_repo: UsersRepository = Depends(get_repository(repo_type=UsersRepository)),
):
    """Guardar todas las preferencias del usuario durante el proceso de onboarding"""
    try:
        # Verificar que el usuario existe
        user = users_repo.get_user_by_id(user_id)
        
        # Save preferences
        result = preferences_repo.save_onboarding_preferences(
            user_id=user_id,
            preference_options=preferences.option_ids,
            weights=preferences.weights
        )
        
        # Mark onboarding as completed
        user_row = users_repo.session.query(UserModel).filter(UserModel.uid == user_id).first()
        if user_row:
            user_row.onboarding_completed = True
            users_repo.session.commit()
        
        return {"success": result, "onboarding_completed": True}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Usuario no encontrado: {str(e)}")
    except Exception as e:
        users_repo.session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.put(
    "/users/{user_id}/categories/{category_id}",
    summary="Update preferences for a specific category",
    status_code=status.HTTP_200_OK,
)
async def update_category_preferences(
    preferences: CategoryPreferences,
    user_id: str = Path(..., title="ID del usuario"),
    category_id: int = Path(..., title="ID de la categoría"),
    preferences_repo: PreferencesRepository = Depends(get_repository(repo_type=PreferencesRepository)),
    users_repo: UsersRepository = Depends(get_repository(repo_type=UsersRepository)),
):
    """Actualizar preferencias para una categoría específica"""
    try:
        # Verificar que el usuario existe
        users_repo.get_user_by_id(user_id)
        
        result = preferences_repo.update_category_preferences(
            user_id=user_id,
            category_id=category_id,
            preference_options=preferences.option_ids,
            weights=preferences.weights
        )
        return {"success": result}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Usuario o categoría no encontrados: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/users/{user_id}/attributes",
    summary="Get user preferences as attributes for ML model",
    response_model=UserPreferencesResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user_preference_attributes(
    user_id: str = Path(..., title="ID del usuario"),
    preferences_repo: PreferencesRepository = Depends(get_repository(repo_type=PreferencesRepository)),
    users_repo: UsersRepository = Depends(get_repository(repo_type=UsersRepository)),
):
    """Obtener las preferencias de un usuario en formato agrupado para el modelo ML"""
    try:
        # Verificar que el usuario existe
        users_repo.get_user_by_id(user_id)
        
        # Obtener preferencias en formato agrupado
        preference_attributes = preferences_repo.get_user_preference_attributes(user_id)
        
        return UserPreferencesResponse(
            user_id=user_id,
            preferences=PreferenceAttributes(**preference_attributes)
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Usuario no encontrado: {str(e)}")
    

@router.get(
    "/users/{user_id}",
    summary="Get user preferences",
    response_model=UserPreferencesResponse,
    status_code=status.HTTP_200_OK,
)
async def get_user_preferences(
    user_id: str = Path(..., title="ID del usuario"),
    preferences_repo: PreferencesRepository = Depends(get_repository(repo_type=PreferencesRepository)),
    users_repo: UsersRepository = Depends(get_repository(repo_type=UsersRepository)),
):
    """Obtener las preferencias de un usuario específico"""
    try:
        # Verificar que el usuario existe
        users_repo.get_user_by_id(user_id)
        
        # Obtener preferencias en formato agrupado (como el modelo espera)
        preference_attributes = preferences_repo.get_user_preference_attributes(user_id)
        
        return UserPreferencesResponse(
            user_id=user_id,
            preferences=PreferenceAttributes(**preference_attributes)
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Usuario no encontrado: {str(e)}")
