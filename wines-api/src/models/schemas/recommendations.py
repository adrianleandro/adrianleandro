from src.models.schemas.base import BaseSchemaModel

class WineRecommendations(BaseSchemaModel):
    user_id: str
    recommendations: list