import fastapi
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import status, Depends, Path, HTTPException, Query
from fastapi.security import HTTPBearer

from src.api.dependencies import get_repository
from src.api.routes.auth import verify_token, oauth2_scheme
from src.repository.users_repository import UsersRepository
from src.repository.preferences_repository import PreferencesRepository
from src.repository.wines_repository import WinesRepository
from src.repository.wine_recommendations_repository import WineRecommendationsRepository
from src.repository.ratings_repository import WineRatingsRepository
from src.utilities.supabase_client import supabase

from src.models.schemas.user import UserPreferences, UserInfo, UserWineRating, UserFavoriteWines
from src.models.schemas.wine import WineFavorites, WineTasted
from src.models.schemas.recommendations import WineRecommendations

from src.api.tasks.summarize_task import SummarizeTask

router = fastapi.APIRouter(prefix="/users", tags=["users"])

# Cache for recommendations: {user_id: (recommendations, timestamp)}
_recommendations_cache = {}
CACHE_EXPIRY_MINUTES = 30  # Cache recommendations for 30 minutes

@router.get(
    '/recommendations',
    summary='Get wine recommendations for a specific user',
    name='recommendations:get-user-recommendations',
    response_model=WineRecommendations,
    status_code=status.HTTP_200_OK,
)
async def get_wine_recommendations(
    user_id: str = Query(..., description="ID of the user to get recommendations for"),
    limit: int = Query(10, description="Maximum number of recommendations to return", ge=1, le=999),
    wine_type: str = Query(None, description="Type of wine to filter recommendations (e.g. tinto, blanco, rosado)"),
    body: str = Query(None, description="Body of wine to filter recommendations (e.g. ligero, medio, robusto)"),
    dryness: str = Query(None, description="Dryness of wine to filter recommendations (e.g. seco, semi-seco, dulce)"),
    country: str = Query(None, description="Country of wine to filter recommendations"),
    abv: float = Query(None, description="Alcohol by volume to filter recommendations"),
    use_cache: bool = Query(True, description="Whether to use cached recommendations if available"),
    users_repo: UsersRepository = Depends(get_repository(repo_type=UsersRepository)),
    preferences_repo: PreferencesRepository = Depends(get_repository(repo_type=PreferencesRepository)),
):
    try:
        # Create cache key based on user_id and filters
        cache_key = f"{user_id}_{limit}_{wine_type}_{body}_{dryness}_{country}_{abv}"
        
        # Check if we have cached recommendations
        if use_cache and cache_key in _recommendations_cache:
            cached_data, timestamp = _recommendations_cache[cache_key]
            
            # Check if cache is still valid
            if datetime.now() - timestamp < timedelta(minutes=CACHE_EXPIRY_MINUTES):
                logging.info(f"Returning cached recommendations for user {user_id}")
                return cached_data
            else:
                # Cache expired, remove it
                logging.info(f"Cache expired for user {user_id}, fetching new recommendations")
                del _recommendations_cache[cache_key]
        
        # Get fresh recommendations
        recommendations_repo = WineRecommendationsRepository()
        user = users_repo.get_user_by_id(user_id)
        recommended_wines = recommendations_repo.get_recommendations(
            user,
            limit,
            wine_type=wine_type,
            body=body,
            dryness=dryness,
            country=country,
            abv=abv
        )
        
        result = WineRecommendations(
            user_id=user_id,
            recommendations=recommended_wines
        )
        
        # Cache the result
        _recommendations_cache[cache_key] = (result, datetime.now())
        logging.info(f"Cached recommendations for user {user_id}")
        
        return result
    except KeyError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    '/{user_id}',
    summary='Get information for a user',
    name='users:get-info',
    response_model=UserInfo,
    status_code=status.HTTP_200_OK,
)
async def get_user_info(
    user_id: str = Path(..., title="The ID of the account to get the info"),
    users_repo: UsersRepository = Depends(get_repository(repo_type=UsersRepository)),
):
    try:
        user = users_repo.get_user_by_id(user_id)
        return UserInfo(uid=user.uid_to_str(), username=user.username, email=user.email, onboarding_completed=user.onboarding_completed)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post(
    '/{user_id}/preferences',
    summary='Post user preferences',
    name='users:post-preferences',
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def update_user_preferences(
    user_preferences: UserPreferences,
    user_id: str = Path(..., title="The ID of the account to update"),
    users_repo: UsersRepository = Depends(get_repository(repo_type=UsersRepository)),
):
    try:
        user = users_repo.get_user_by_id(user_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    user.username = user_preferences.name
    user.add_preferences(user_preferences.list_values())
    return users_repo.save(user)

@router.get(
    '/{user_id}/wines/status',
    summary='Get user rated and favorite wines',
    name='users:get-favorites',
    response_model=list,
    status_code=status.HTTP_200_OK,
)
async def get_user_favorites(
    user_id: str = Path(..., title="The ID of the user getting the favorites"),
    users_repo: UsersRepository = Depends(get_repository(repo_type=UsersRepository)),
):
    try:
        user = users_repo.get_user_by_id(user_id)
        return UserFavoriteWines(favorite_wines=[
            WineFavorites(
                id=wine.id,
                name=wine.name,
                type=wine.type,
                elaborate=wine.elaborate,
                abv=wine.abv,
                body=wine.body,
                country=wine.country,
                region=wine.region,
                winery=wine.winery,
            ) for wine in user.get_favorites()],
            tasted_wines=[
            WineTasted(
                id=rating.wine_id,
                name=rating.wine.name,
                type=rating.wine.type,
                elaborate=rating.wine.elaborate,
                abv=rating.wine.abv,
                body=rating.wine.body,
                country=rating.wine.country,
                region=rating.wine.region,
                winery=rating.wine.winery,
                rating=rating.rating,
            ) for rating in user.get_ratings()])
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    '/{user_id}/wines/status/{wine_id}',
    summary='Get user rating for a selected wine',
    name='users:get-favorites',
    response_model=UserWineRating,
    status_code=status.HTTP_200_OK,
)
async def get_user_rating(
    user_id: str = Path(..., title="The ID of the user getting the favorites"),
    wine_id: int = Path(..., title="The ID of the wine"),
    users_repo: UsersRepository = Depends(get_repository(repo_type=UsersRepository)),
):
    try:
        user = users_repo.get_user_by_id(user_id)
        rating = user.get_ratings(wine_id)
        if not rating:
            tasted = False
            user_rating = None
            user_review = None
        else:
            tasted = True
            user_rating = rating.rating
            user_review = rating.review
        return UserWineRating(
            wine=wine_id,
            tasted=tasted,
            is_favorite=wine_id in [f.id for f in user.get_favorites()],
            rating=user_rating,
            review=user_review
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
    '/{user_id}/wines/status',
    summary='Post user tasted and rated wine',
    name='users:post-ratings',
    response_model=None,
    status_code=status.HTTP_201_CREATED,
)
async def post_user_rating(
    user_rating: UserWineRating,
    user_id: str = Path(..., title="The ID of the user posting the rating"),
    users_repo: UsersRepository = Depends(get_repository(repo_type=UsersRepository)),
    ratings_repo: WineRatingsRepository = Depends(get_repository(repo_type=WineRatingsRepository)),
    summarizer: SummarizeTask = Depends(SummarizeTask),
):
    try:
        user = users_repo.get_user_by_id(user_id)
        wine = WinesRepository().get_by_id(user_rating.wine)
        rating = user.rate_wine(wine, user_rating.rating, user_rating.review)
        if ratings_repo.save(rating):
            if user_rating.review:
                all_ratings = ratings_repo.get_by_wine_id(wine.wine_id)
                summarizer.schedule_summary(wine.wine_id, all_ratings)
                return
        else:
            raise HTTPException(status_code=500, detail='Error saving rating. Please try again later.')
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
    '/{user_id}/favorites/{wine_id}',
    summary='Post user favorite wine',
    name='users:post-favorites',
    response_model=None,
    status_code=status.HTTP_201_CREATED,
)
async def post_user_favorite(
    user_id: str = Path(..., title="The ID of the user posting the favorite wine"),
    wine_id: int = Path(..., title="The ID of the wine marked as favorite"),
    users_repo: UsersRepository = Depends(get_repository(repo_type=UsersRepository))
):
    try:
        wines_repo = WinesRepository()
        user = users_repo.get_user_by_id(user_id)
        wine = wines_repo.get_by_id(wine_id)
        user.add_favorite(wine)
        users_repo.save(user)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete(
    '/{user_id}/favorites/{wine_id}',
    summary='Delete user favorite wine',
    name='users:post-favorites',
    response_model=None,
    status_code=status.HTTP_200_OK,
)
async def delete_user_favorite(
    user_id: str = Path(..., title="The ID of the user deleting the favorite wine"),
    wine_id: int = Path(..., title="The ID of the wine marked as favorite"),
    users_repo: UsersRepository = Depends(get_repository(repo_type=UsersRepository))
):
    try:
        user = users_repo.get_user_by_id(user_id)
        users_repo.delete_favorite_wine(user, wine_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/complete-onboarding")
async def complete_onboarding(token: HTTPBearer = Depends(oauth2_scheme)):
    try:
        # Verificar el token y obtener el usuario
        user = verify_token(token.credentials)
        user_id = user.id
        
        # Actualizar el campo onboarding_completed a True
        response = supabase.table("users").update(
            {"onboarding_completed": True}
        ).eq("uid", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        return {"message": "Onboarding completado exitosamente"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))