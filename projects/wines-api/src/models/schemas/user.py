from pydantic import EmailStr
from src.models.schemas.base import BaseSchemaModel

class UserPreferences(BaseSchemaModel):
    name: str
    type: int
    body: int
    intensity: int
    dryness: int
    abv: int

    def list_values(self):
        return [self.type, self.body, self.intensity, self.dryness, self.abv]

class UserInfo(BaseSchemaModel):
    uid: str
    username: str
    email: str
    onboarding_completed: bool

class UserWineRating(BaseSchemaModel):
    wine: int
    tasted: bool = False
    is_favorite: bool = False
    rating: int | None = None
    review: str | None = None

class UserFavoriteWines(BaseSchemaModel):
    favorite_wines: list
    tasted_wines: list

class UserCreate(BaseSchemaModel):
    email: EmailStr
    password: str

class UserLogin(BaseSchemaModel):
    email: EmailStr
    password: str

class LoginResponse(BaseSchemaModel):
    access_token: str
    token_type: str
    user_id: str
    onboarding_completed: bool
    refresh_token: str

class RefreshRequest(BaseSchemaModel):
    refresh_token: str

class RefreshResponse(BaseSchemaModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
