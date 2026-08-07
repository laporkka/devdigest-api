from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.users import UserCreate
from models.models import User
from core.security import get_password_hash


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    return user


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)

    new_user = User(
        email=user_in.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
