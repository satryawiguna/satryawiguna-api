"""
Blog post schemas for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class BlogPostBase(BaseModel):
    """Base blog post schema"""
    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    excerpt: Optional[str] = None
    content: Optional[str] = None
    thumbnail_url: Optional[str] = None
    image_url: Optional[str] = None
    status: str = Field(default="draft", max_length=50)


class BlogPostCreate(BlogPostBase):
    """Schema for creating a blog post"""
    author_id: Optional[int] = None
    category_ids: Optional[List[int]] = []
    tag_ids: Optional[List[int]] = []


class BlogPostUpdate(BaseModel):
    """Schema for updating a blog post"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    excerpt: Optional[str] = None
    content: Optional[str] = None
    thumbnail_url: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)
    published_at: Optional[datetime] = None
    category_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None


class BlogPostResponse(BlogPostBase):
    """Schema for blog post response"""
    id: int
    author_id: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    categories: List["CategoryResponse"] = Field(default=[], validation_alias="blog_post_categories")
    tags: List["TagResponse"] = Field(default=[], validation_alias="blog_post_tags")

    @field_validator('categories', mode='before')
    @classmethod
    def extract_categories(cls, v):
        if not v:
            return []
        result = []
        for item in v:
            if hasattr(item, 'category') and item.category is not None:
                result.append({
                    'id': item.category.id,
                    'name': item.category.name,
                    'slug': item.category.slug,
                    'type': getattr(item.category, 'type', 'BLOG_POST'),
                })
            elif isinstance(item, dict):
                result.append(item)
            else:
                result.append(item)
        return result

    @field_validator('tags', mode='before')
    @classmethod
    def extract_tags(cls, v):
        if not v:
            return []
        result = []
        for item in v:
            if hasattr(item, 'tag') and item.tag is not None:
                result.append({
                    'id': item.tag.id,
                    'name': item.tag.name,
                    'slug': item.tag.slug,
                })
            elif isinstance(item, dict):
                result.append(item)
            else:
                result.append(item)
        return result
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    type: str = Field(default="BLOG_POST", max_length=20)


class CategoryCreate(CategoryBase):
    """Schema for creating a category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, max_length=20)


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


class TagUpdate(BaseModel):
    """Schema for updating a tag"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)


class TagResponse(TagBase):
    """Schema for tag response"""
    id: int
    
    class Config:
        from_attributes = True


BlogPostResponse.model_rebuild()

