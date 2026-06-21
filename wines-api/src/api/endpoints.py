import fastapi

from src.api.routes.users import router as users_router
from src.api.routes.preferences import router as preferences_router
from src.api.routes.wines import router as wines_router
from src.api.routes.auth import router as auth_router, oauth2_scheme

public_router = fastapi.APIRouter()
router = fastapi.APIRouter(dependencies=[fastapi.Depends(oauth2_scheme)])

@public_router.get('/')
async def get_app_info():
    return {
        'appName': 'tuVino',
        'version': '0.0.1',
    }

router.include_router(router=users_router)
router.include_router(router=preferences_router)
router.include_router(router=wines_router)
public_router.include_router(router=auth_router)