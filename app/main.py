from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.models import Tag
from app.api.users import router as users_router
from app.api.tags import router as tags_router
from app.api.arlicles import router as article_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        query = select(Tag)
        result = await session.execute(query)
        tags = result.scalars().all()

        if not tags:
            default_tags = [
                Tag(name="python"), 
                Tag(name="fastapi"), 
                Tag(name="ai"), 
                Tag(name="docker"), 
                Tag(name="redis"), 
                Tag(name="alembic"), 
                Tag(name="postgresql")
            ]

            session.add_all(default_tags)
            await session.commit()

            print("🌱 База данных успешно заполнена дефолтными тегами!")

        yield 

   
app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=True,       
    allow_methods=["*"],          
    allow_headers=["*"],          
)


app.include_router(users_router)
app.include_router(tags_router)
app.include_router(article_router)


@app.get("/")
async def root():
    return {
        "status": "ok", 
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }