from app.extensions import db
from typing import List
from flask_login import UserMixin
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Column, ForeignKey, Table

class Category(db.Model):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    blogs: Mapped[List["Blog"]] = relationship(secondary='blog_categories', back_populates="categories_list")

class Blog(db.Model):
    __tablename__ = 'blogs'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(500))
    body: Mapped[str] = mapped_column(Text)
    date: Mapped[str] = mapped_column(String(50), nullable=False)
    featured_image: Mapped[str] = mapped_column(String(500))
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="blogs")
    categories_list: Mapped[List["Category"]] = relationship(secondary='blog_categories', back_populates="blogs")

class PortfolioEntry(db.Model):
    __tablename__ = 'portfolio_entries'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    external_url: Mapped[str] = mapped_column(String(500))
    image: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    tooling: Mapped[str] = mapped_column(Text)
    responsibilities: Mapped[str] = mapped_column(Text)

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    blogs: Mapped[List["Blog"]] = relationship(back_populates="author")

blog_categories = Table(
    'blog_categories', db.metadata,
    Column('blog_id', Integer, ForeignKey("blogs.id"), primary_key=True),
    Column('category_id', Integer, ForeignKey("categories.id"), primary_key=True)
)
