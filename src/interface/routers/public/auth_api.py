# filepath: src/interface/routers/public/auth_api.py
from fastapi import APIRouter, Depends, Response, Cookie, HTTPException, status
from interface.dependencies import get_auth_service
from interface.schemas.auth_schema import UserCreate, UserRead, LoginRequest, TokenPair
from core.services.auth_service import AuthService
from core.entites.auth_entity import User as UserEntity
from core.exceptions import AuthenticationError, DuplicateEntryError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRead:
    try:
        user_entity = UserEntity(
            username=user_data.username,
            email=user_data.email,
            password_hash=user_data.password,
            is_active=True,
        )
        created = await auth_service.create_user(user_entity)
        return created
    except DuplicateEntryError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    "/login",
    response_model=TokenPair,
)
async def login(
    login_data: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    try:
        tokens = await auth_service.login(login_data.email, login_data.password)
        response.set_cookie(
            key="access_token",
            value=tokens.access_token.token,
            httponly=True,
            secure=True,
            samesite="strict",
            expires=int(tokens.access_token.expires_at.timestamp()),
        )
        print(tokens.access_token.expires_at.timestamp())
        response.set_cookie(
            key="refresh_token",
            value=tokens.refresh_token.token,
            httponly=True,
            secure=True,
            samesite="strict",
            expires=int(tokens.refresh_token.expires_at.timestamp()),
        )
        return TokenPair(
            access_token=tokens.access_token.token,
            refresh_token=tokens.refresh_token.token,
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post(
    "/refresh",
    response_model=TokenPair,
)
async def refresh(
    response: Response,
    refresh_token: str = Cookie(None),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )
    try:
        tokens = await auth_service.refresh_tokens(refresh_token)
        response.set_cookie(
            key="refresh_token",
            value=tokens.refresh_token.token,
            httponly=True,
            secure=True,
            samesite="strict",
            expires=int(tokens.refresh_token.expires_at.timestamp()),
        )
        return TokenPair(
            access_token=tokens.access_token.token,
            refresh_token=tokens.refresh_token.token,
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    response: Response,
    refresh_token: str = Cookie(None),
    auth_service: AuthService = Depends(get_auth_service),
):
    if refresh_token:
        await auth_service.logout(refresh_token)
    response.delete_cookie(key="refresh_token")
