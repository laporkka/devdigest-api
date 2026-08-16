from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.models.models import Tag, User, UserTag
from app.core.database import get_db
from app.schemas.tags import TagsResponse


router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=list[TagsResponse])
async def get_all_tags(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Tag)
    result = await db.execute(query)
    tags = result.scalars().all()

    return tags


@router.get("/my_tags", response_model=list[TagsResponse])
async def get_my_tags(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Tag).join(UserTag, Tag.id == UserTag.tag_id).where(UserTag.user_id == current_user.id)
    result = await db.execute(query)
    my_tags = result.scalars().all()

    return my_tags


@router.post("/subscribe/{tag_id}", response_model=dict)
async def tag_subscribe(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tag_query = select(Tag).where(Tag.id == tag_id)
    tag_result = await db.execute(tag_query)
    existing_tag = tag_result.scalar_one_or_none()

    if existing_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
        
    
    query = select(UserTag).where(UserTag.user_id == current_user.id, UserTag.tag_id == tag_id)
    result = await db.execute(query)
    existing_sub = result.scalar_one_or_none()

    if existing_sub:
        raise HTTPException(status_code=400, detail="Already subscribed to this tag")

    new_subscription = UserTag(
        user_id=current_user.id,
        tag_id=tag_id
    )

    db.add(new_subscription)
    await db.commit()

    return {"status": "success", "message": "Subscribed successfully"}


@router.post("/unsubscribe/{tag_id}", response_model=dict)
async def tag_unsubscribe(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(UserTag).where(UserTag.user_id == current_user.id, UserTag.tag_id == tag_id)
    result = await db.execute(query)
    subscribe_tag = result.scalar_one_or_none()

    if subscribe_tag is None:
        raise HTTPException(status_code=400, detail="Not subscribed to this tag")

    await db.delete(subscribe_tag)
    await db.commit()

    return {"status": "success", "message": "Subscribe was deleted"}