import asyncio
import httpx
from celery import shared_task
from sqlalchemy import select

from core.database import AsyncSessionLocal
from app.models.models import Tag, Article


async def fetch_story_details(client: httpx.AsyncClient, story_id: int) -> dict | None:
    url = f"https://firebaseio.com{story_id}.json"

    response = await client.get(url)

    if response.status_code == 200:
        return response.json()

    return None


async def run_parser():
    async with httpx.AsyncClient() as client:
        try:
            top_stories_response = await client.get("https://firebase.com", timeout=5.0)
            story_ids = top_stories_response.json()[:30]

        except Exception as e:
            print(f"Не удалось получить топ историй: {e}")
            return

        tasks = [fetch_story_details(client, s_id) for s_id in story_ids]
        stories = await asyncio.gather(*tasks)

    async with AsyncSessionLocal() as session:
        query = select(Tag)
        result = await session.execute(query)
        tags_objects = result.scalars().all()

        allowed_tags = [t.name.lower() for t in tags_objects]

        if not allowed_tags:
            allowed_tags = ["python", "fastapi", "ai", "rust", "docker"]


        for story in stories:
            if not story:
                continue

            title = story.get("title")
            url = story.get("url")
            likes = story.get("score", 0)
            comments = story.get("descendants", 0)

            if not title or not url:
                continue

            hype_score = likes + (comments * 2)

            title_lower = title.lower()
            has_matching_tag  = any(tag in title_lower for tag in allowed_tags)

            if has_matching_tag:
                query = select(Article).where(Article.url == url)
                result = await session.execute(query)
                article = result.scalar_one_or_none()

                if article:
                    if hype_score > article.score:
                        article.score = hype_score
       
                else:
                    new_article = Article(
                        title=title,
                        url=url,
                        source="hackernews",
                        score=hype_score
                    )

                    session.add(new_article)

        await session.commit()
        print("Парсер HackerNews успешно завершил работу.")
                    

@shared_task(name="tasks.parse_hackernews")
def parse_hackernews():
    asyncio.run(run_parser())

