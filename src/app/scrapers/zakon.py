"""Парсер новостей с сайта Zakon.kz."""
import time

import httpx
from bs4 import BeautifulSoup

from app.scrapers.base import ArticleData, BaseScraper

BASE_URL = "https://www.zakon.kz"
NEWS_URL = f"{BASE_URL}/busin/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ContentFlow/1.0",
}
TIMEOUT = 15
DELAY = 1.5  # секунд между запросами


class ZakonScraper(BaseScraper):
    """Парсит список новостей и каждую статью с Zakon.kz."""

    def fetch_articles(self) -> list[ArticleData]:
        """Главный метод: получить ссылки со страницы, потом спарсить каждую."""
        links = self._get_article_links()
        articles = []

        for link in links[:15]:  # берём не больше 15, чтобы не нагружать сайт
            time.sleep(DELAY)
            article = self._parse_article(link)
            if article:
                articles.append(article)

        return articles

    def _get_article_links(self) -> list[str]:
        """Достать ссылки на статьи со страницы списка новостей."""
        try:
            response = httpx.get(NEWS_URL, headers=HEADERS, timeout=TIMEOUT, follow_redirects=True)
            response.raise_for_status()
        except httpx.HTTPError:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        links = []

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            # Берём только ссылки на статьи (обычно содержат /news/ или числовой путь)
            if "/busin/" in href and href != "/busin/" and href not in links:
                # Делаем ссылку полной
                if href.startswith("/"):
                    href = BASE_URL + href
                if href.startswith(BASE_URL) and href not in links:
                    links.append(href)

        return links[:30]

    def _parse_article(self, url: str) -> ArticleData | None:
        """Спарсить одну статью по URL."""
        try:
            response = httpx.get(url, headers=HEADERS, timeout=TIMEOUT, follow_redirects=True)
            response.raise_for_status()
        except httpx.HTTPError:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Заголовок
        h1 = soup.find("h1")
        if not h1:
            return None
        title = h1.get_text(strip=True)

        # Тело статьи — ищем основной контейнер
        body = soup.find("article") or soup.find("div", class_="article")
        if body:
            # Убираем скрипты и стили внутри
            for tag in body.find_all(["script", "style"]):
                tag.decompose()
            content = body.get_text(separator="\n", strip=True)
        else:
            content = ""

        # Краткое описание — первые 300 символов контента
        summary = content[:300] if content else None

        # Дата — ищем тег <time> или meta
        published_at = None
        time_tag = soup.find("time")
        if time_tag and time_tag.get("datetime"):
            from datetime import datetime
            dt_str = time_tag["datetime"]
            for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    published_at = datetime.strptime(dt_str[:len(fmt) + 5], fmt)
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
