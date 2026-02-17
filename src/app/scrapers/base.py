from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ArticleData:
    title: str
    url: str
    summary: str | None = None
    content: str | None = None
    published_at: datetime | None = None


class BaseScraper(ABC):
    @abstractmethod
    def fetch_articles(self) -> list[ArticleData]:
        pass
