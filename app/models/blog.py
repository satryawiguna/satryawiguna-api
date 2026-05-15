"""
BlogPost, Category, Tag and related models
"""
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class BlogPost(Base):
    """BlogPost model"""
    __tablename__ = "blog_posts"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    excerpt = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    featured_image_url = Column(String(500), nullable=True)
    author_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False, default="draft")
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="blog_posts", foreign_keys=[author_id])
    blog_post_categories = relationship("BlogPostCategory", back_populates="blog_post", cascade="all, delete-orphan")
    blog_post_tags = relationship("BlogPostTag", back_populates="blog_post", cascade="all, delete-orphan")


class Category(Base):
    """Category model"""
    __tablename__ = "categories"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    
    # Relationships
    blog_post_categories = relationship("BlogPostCategory", back_populates="category", cascade="all, delete-orphan")


class BlogPostCategory(Base):
    """BlogPostCategory model (pivot table)"""
    __tablename__ = "blog_post_categories"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    post_id = Column(BigInteger, ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(BigInteger, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    blog_post = relationship("BlogPost", back_populates="blog_post_categories")
    category = relationship("Category", back_populates="blog_post_categories")


class Tag(Base):
    """Tag model"""
    __tablename__ = "tags"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    
    # Relationships
    blog_post_tags = relationship("BlogPostTag", back_populates="tag", cascade="all, delete-orphan")


class BlogPostTag(Base):
    """BlogPostTag model (pivot table)"""
    __tablename__ = "blog_post_tags"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    post_id = Column(BigInteger, ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(BigInteger, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    blog_post = relationship("BlogPost", back_populates="blog_post_tags")
    tag = relationship("Tag", back_populates="blog_post_tags")
