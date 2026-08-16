from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.models import Article, Tag, UserTag, User
from app.schemas.articles import ArticleResponse


router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("/feed", response_model=list[ArticleResponse])
async def get_user_news_feed(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tag_query = select(Tag.name).join(UserTag, Tag.id == UserTag.tag_id).where(UserTag.user_id == current_user.id)
    tag_result = await db.execute(tag_query)
    user_tags = tag_result.scalars().all()

    if not user_tags:
        return []

    conditions = [Article.title.ilike(f"%{tag_name}%") for tag_name in user_tags]

    article_query = select(Article).where(*conditions).order_by(Article.score.desc())
    article_result = await db.execute(article_query)
    articles = article_result.scalars().all()

    return articles