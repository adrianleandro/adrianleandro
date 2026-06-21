import fastapi
import logging
from fastapi import UploadFile, File, Form, HTTPException, Depends, status
import os
from datetime import datetime

from src.api.dependencies import get_repository
from src.repository.users_repository import UsersRepository
from src.repository.wine_recommendations_repository import WineRecommendationsRepository
from src.services.ocr_service import OCRService
from src.services.menu_recommendation_service import MenuRecommendationService
from src.models.schemas.menu import MenuRecommendationResponse, MenuWineRecommendation, MenuParseRequest
import base64

router = fastapi.APIRouter(prefix="/menu", tags=["menu"])

@router.post(
    "/parse",
    summary="Parse wine menu from image and get personalized recommendations",
    response_model=MenuRecommendationResponse,
    status_code=status.HTTP_201_CREATED
)
async def parse_menu_and_recommend(
    request: MenuParseRequest,
    users_repo: UsersRepository = Depends(get_repository(repo_type=UsersRepository)),
):
    """
    Upload a restaurant menu image and get personalized wine recommendations
    based on the user's taste preferences.
    
    The service will:
    1. Extract text from the menu using OCR
    2. Fetch the user's top wine recommendations
    3. Use AI to match menu wines with user preferences
    4. Return top 3 recommendations with explanations
    """
    try:
        # Validate user exists
        user = users_repo.get_user_by_id(request.user_id)
        
        # Decode base64 image and save temporarily
        timestamp = datetime.now().timestamp()
        temp_filename = f"{timestamp}_menu.jpg"
        temp_path = f"/tmp/{temp_filename}"
        
        try:
            image_data = base64.b64decode(request.image_base64)
            with open(temp_path, "wb") as buffer:
                buffer.write(image_data)
        except Exception as decode_error:
            logging.error(f"Failed to decode base64 image: {str(decode_error)}")
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        logging.info(f"Saved temporary image: {temp_path}")
        
        # Step 1: Extract text from image using OCR
        logging.info(f"Extracting text from menu for user {request.user_id}")
        ocr_service = OCRService()
        menu_text = await ocr_service.extract_menu_text(temp_path)
        logging.info(f"Extracted {len(menu_text)} characters from menu")
        
        # Step 2: Get user's top wine recommendations
        logging.info(f"Fetching top recommendations for user {request.user_id}")
        recommendations_repo = WineRecommendationsRepository()
        top_wines = recommendations_repo.get_recommendations(user, limit=5)
        
        # Convert to dict format (handle both schema objects and dicts)
        top_wines_dict = []
        for wine in top_wines:
            # Handle WineSchema objects (use dict() or model_dump())
            if hasattr(wine, 'model_dump'):
                wine_dict = wine.model_dump()
            elif hasattr(wine, 'dict'):
                wine_dict = wine.dict()
            else:
                wine_dict = {
                    "name": getattr(wine, 'wine_name', getattr(wine, 'name', 'Unknown')),
                    "type": getattr(wine, 'wine_type', getattr(wine, 'type', 'Unknown')),
                    "body": getattr(wine, 'body', 'N/A'),
                    "region": getattr(wine, 'region', 'N/A'),
                    "abv": getattr(wine, 'abv', 'N/A'),
                    "winery": getattr(wine, 'winery', 'N/A')
                }
            
            # Ensure we have the expected keys
            top_wines_dict.append({
                "name": wine_dict.get('wine_name', wine_dict.get('name', 'Unknown')),
                "type": wine_dict.get('wine_type', wine_dict.get('type', 'Unknown')),
                "body": wine_dict.get('body', 'N/A'),
                "region": wine_dict.get('region', 'N/A'),
                "abv": wine_dict.get('abv', 'N/A'),
                "winery": wine_dict.get('winery', 'N/A')
            })
        
        logging.info(f"Retrieved {len(top_wines_dict)} top wines for user")
        
        # Step 3: Use LLM to match menu wines with user preferences
        logging.info(f"Generating AI recommendations for user {request.user_id}")
        recommendation_service = MenuRecommendationService()
        llm_result = await recommendation_service.get_menu_recommendations(
            menu_text=menu_text,
            user_top_wines=top_wines_dict
        )
        logging.info(f"Generated {len(llm_result.get('recommendations', []))} recommendations")
        
        # Clean up temp file
        try:
            os.remove(temp_path)
            logging.info(f"Cleaned up temporary file: {temp_path}")
        except Exception as cleanup_error:
            logging.warning(f"Failed to clean up temp file: {str(cleanup_error)}")
        
        # Format response
        recommendations = [
            MenuWineRecommendation(**rec)
            for rec in llm_result.get("recommendations", [])
        ]
        
        return MenuRecommendationResponse(
            summary=llm_result.get("summary", ""),
            recommendations=recommendations
        )
        
    except KeyError as e:
        logging.error(f"User not found: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Usuario no encontrado: {str(e)}")
    except Exception as e:
        logging.error(f"Menu parsing error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error procesando el menú: {str(e)}")

