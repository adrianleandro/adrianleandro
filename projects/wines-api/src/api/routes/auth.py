from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from src.utilities.supabase_client import supabase
from src.models.schemas.user import UserCreate, UserLogin, LoginResponse, RefreshResponse, RefreshRequest
from src.repository.users_repository import UsersRepository
from src.api.dependencies import get_repository
from src.repository.table_models import User as UserModel

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(
    user_data: UserCreate,
    users_repo: UsersRepository = Depends(get_repository(repo_type=UsersRepository))
):
    supabase_user_id = None
    
    try:
        # Register with Supabase Auth
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password
        })
        
        if response.user is None:
            raise HTTPException(status_code=400, detail="No se pudo registrar al usuario.")
        
        supabase_user_id = response.user.id
        
    except Exception as e:
        error_msg = str(e)
        # Supabase throws exception when user already exists in Auth
        if "User already registered" in error_msg or "already been registered" in error_msg:
            raise HTTPException(status_code=400, detail="El usuario ya está registrado.")
        raise HTTPException(status_code=400, detail=f"Error en Supabase Auth: {error_msg}")
    
    # Now insert into PostgreSQL users table
    try:
        # Check if user already exists in PostgreSQL
        existing_user = users_repo.session.query(UserModel).filter(
            UserModel.uid == supabase_user_id
        ).first()
        
        if not existing_user:
            new_user = UserModel(
                uid=supabase_user_id,
                email=user_data.email,
                name=user_data.email.split('@')[0],
                onboarding_completed=False
            )
            users_repo.session.add(new_user)
            users_repo.session.commit()
            
    except Exception as e:
        users_repo.session.rollback()
        raise HTTPException(status_code=400, detail=f"Error al guardar usuario: {str(e)}")

    return {
        "message": "Usuario registrado exitosamente.",
        "user_id": supabase_user_id
    }


@router.post("/login", response_model=LoginResponse)
async def login(
    user_data: UserLogin,
    users_repo: UsersRepository = Depends(get_repository(repo_type=UsersRepository))
):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password,
        })
        if response.session is None:
            raise HTTPException(status_code=401, detail="Credenciales inválidas.")
            
        user_id = response.user.id
        
        # Get user data from PostgreSQL instead of Supabase
        user_row = users_repo.session.query(UserModel).filter(UserModel.uid == user_id).first()
        if not user_row:
            raise HTTPException(status_code=404, detail="Usuario no encontrado en la base de datos.")
        
        onboarding_completed = user_row.onboarding_completed
        user_name = user_row.name
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return LoginResponse(
        access_token=response.session.access_token,
        refresh_token=response.session.refresh_token,
        token_type="bearer",
        user_id=user_id,
        user_name=user_name,
        onboarding_completed=onboarding_completed
    )

@router.post("/refresh", response_model=RefreshResponse)
def refresh_token(refresh_data: RefreshRequest):
    if not refresh_data.refresh_token:
        raise HTTPException(status_code=400, detail="No se proporcionó refresh_token")

    try:
        response = supabase.auth.refresh_session(refresh_data.refresh_token)

        if response.session is None:
            raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


def verify_token(token: str) -> dict:
    """Verifica el token JWT con Supabase y devuelve los datos del usuario o lanza una excepción."""
    try:
        user_response = supabase.auth.get_user(token)

        if user_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado",
            )
        return user_response.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"No se pudo validar el token: {e}",
        )

oauth2_scheme = HTTPBearer()