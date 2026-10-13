from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base

# Many-to-many table for user-selected sections
user_sections = Table(
    "user_sections",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("section_id", Integer, ForeignKey("sections.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    github_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to sections via user_sections table
    sections = relationship("Section", secondary=user_sections, backref="users")

class UserTopic(Base):
    __tablename__ = "user_topics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)

class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    sources = relationship("Source", back_populates="section")

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    name = Column(String, nullable=False)
    feed_url = Column(Text, nullable=False)
    kind = Column(String, default="rss", nullable=False)

    section = relationship("Section", back_populates="sources")
    articles = relationship("Article", back_populates="source")

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    snippet = Column(Text)
    published_at = Column(DateTime(timezone=True))
    embedding = Column(Vector(1536))
    cluster_id = Column(Integer)

    source = relationship("Source", back_populates="articles")
