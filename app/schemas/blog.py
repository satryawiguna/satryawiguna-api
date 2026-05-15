"""
Blog post schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BlogPostBase(BaseModel):
    """Base blog post schema"""
    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    excerpt: Optional[str] = None
    content: Optional[str] = None
    featured_image_url: Optional[str] = None
    status: str = Field(default="draft", max_length=50)


class BlogPostCreate(BlogPostBase):
    """Schema for creating a blog post"""
    author_id: int


class BlogPostUpdate(BaseModel):
    """Schema for updating a blog post"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    excerpt: Optional[str] = None
    content: Optional[str] = None
    featured_image_url: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)
    published_at: Optional[datetime] = None


class BlogPostResponse(BlogPostBase):
    """Schema for blog post response"""
    id: int
    author_id: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)


class CategoryCreate(CategoryBase):
    """Schema for creating a category"""
    pass


class CategoryResponse(CategoryBase):
    """Schema for category response"""
    id: int
    
    class Config:
        from_attributes = True


class TagBase(BaseModel):
    """Base tag schema"""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)


class TagCreate(TagBase):
    """Schema for creating a tag"""
    pass


class TagResponse(TagBase):
    """Schema for tag response"""
    id: int
    
    class Config:
        from_attributes = True
