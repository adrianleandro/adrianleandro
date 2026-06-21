from pydantic import BaseModel
from typing import List, Optional

class MenuParseRequest(BaseModel):
    user_id: str
    image_base64: str  # Base64 encoded image

class MenuWineRecommendation(BaseModel):
    wine_name: str
    reason: str
    estimated_price: Optional[str] = None
    wine_type: Optional[str] = None

class MenuRecommendationResponse(BaseModel):
    summary: str  # LLM-generated summary
    recommendations: List[MenuWineRecommendation]
