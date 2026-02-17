from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(1024), nullable=False)
    url = Column(String(2048), nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    source = relationship("Source", back_populates="articles")

    __table_args__ = (UniqueConstraint("source_id", "url", name="uq_article_source_url"),)
