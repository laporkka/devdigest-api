from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.users import UserCreate, UserResponse
from app.schemas.users import Token
from app.services.users import get_user_by_email, create_user
from app.core.security import verify_password, create_access_token


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    existing_user = await get_user_by_email(db, user_in.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = await create_user(db, user_in)

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, user_in.email)

    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not exist",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token({"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}

    
    
