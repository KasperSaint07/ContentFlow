import time
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


class ZakonScraper(BaseScraper):
    def fetch_articles(self) -> list[ArticleData]:
        links = self._get_article_links()
        articles = []

        for link in links[:15]:
            time.sleep(DELAY)
            article = self._parse_article(link)
            if article:
                articles.append(article)

        return articles

    def _get_article_links(self) -> list[str]:
        try:
            response = httpx.get(NEWS_URL, headers=HEADERS, timeout=TIMEOUT, follow_redirects=True)
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

        return links[:30]

    def _parse_article(self, url: str) -> ArticleData | None:
        try:
            response = httpx.get(url, headers=HEADERS, timeout=TIMEOUT, follow_redirects=True)
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
