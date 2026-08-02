from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/docs"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=True,       
    allow_methods=["*"],          
    allow_headers=["*"],          
)


@app.get("/")
async def root():
    return {"status": "ok", "project": settings.PROJECT_NAME}