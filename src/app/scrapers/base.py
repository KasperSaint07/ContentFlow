"""Базовый класс для парсеров и данные одной статьи."""
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod


@dataclass
class ArticleData:
    """Данные статьи до сохранения в БД (то, что вернул парсер)."""
    title: str
    url: str
    summary: str | None = None
    content: str | None = None
    published_at: datetime | None = None


class BaseScraper(ABC):
    """Базовый класс парсера. Каждый сайт — свой класс-наследник."""

    @abstractmethod
    def fetch_articles(self) -> list[ArticleData]:
        """Спарсить статьи с сайта и вернуть список ArticleData."""
        pass
