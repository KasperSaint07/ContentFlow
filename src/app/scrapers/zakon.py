import asyncio
from datetime import datetime
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.scrapers.base import ArticleData, BaseScraper

BASE_URL = "https://www.zakon.kz"
NEWS_URL = BASE_URL

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ContentFlow/1.0",
}
TIMEOUT = 15
DELAY = 1.5
MAX_LINKS_SCAN = 200
MAX_ARTICLES_PER_RUN = 50
MAX_CONCURRENT_REQUESTS = 5


class ZakonScraper(BaseScraper):
    def fetch_articles(self) -> list[ArticleData]:
        return asyncio.run(self._fetch_articles_async())

    async def _fetch_articles_async(self) -> list[ArticleData]:
        async with httpx.AsyncClient(
            headers=HEADERS,
            timeout=TIMEOUT,
            follow_redirects=True,
        ) as client:
            links = await self._get_article_links(client)
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
            tasks = [
                self._parse_article(client, link, semaphore)
                for link in links[:MAX_ARTICLES_PER_RUN]
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        articles: list[ArticleData] = []
        for result in results:
            if isinstance(result, ArticleData):
                articles.append(result)
        return articles

    async def _get_article_links(self, client: httpx.AsyncClient) -> list[str]:
        try:
            response = await client.get(NEWS_URL)
            response.raise_for_status()
        except httpx.HTTPError:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        links: list[str] = []
        seen: set[str] = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag.get("href")
            if not href or href.startswith("#"):
                continue

            full_url = urljoin(BASE_URL, href)
            if not full_url.startswith(BASE_URL):
                continue

            if not full_url.endswith(".html"):
                continue

            if full_url in seen:
                continue

            seen.add(full_url)
            links.append(full_url)

        return links[:MAX_LINKS_SCAN]

    async def _parse_article(
        self,
        client: httpx.AsyncClient,
        url: str,
        semaphore: asyncio.Semaphore,
    ) -> ArticleData | None:
        try:
            async with semaphore:
                await asyncio.sleep(DELAY)
                response = await client.get(url)
                response.raise_for_status()
        except httpx.HTTPError:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        h1 = soup.find("h1")
        if not h1:
            return None
        title = h1.get_text(strip=True)

        body = (
            soup.find("article")
            or soup.find("div", class_=lambda c: c and ("article" in c or "content" in c))
        )
        if body:
            for tag in body.find_all(["script", "style"]):
                tag.decompose()
            content = body.get_text(separator="\n", strip=True)
        else:
            content = ""

        summary = content[:300] if content else None

        published_at = None
        time_tag = soup.find("time")
        if time_tag and time_tag.get("datetime"):
            dt_str = time_tag["datetime"]
            try:
                published_at = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            except ValueError:
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                    try:
                        published_at = datetime.strptime(dt_str[:19], fmt)
                        break
                    except ValueError:
                        continue

        if not title:
            return None

        return ArticleData(
            title=title,
            url=url,
            summary=summary,
            content=content or None,
            published_at=published_at,
        )
