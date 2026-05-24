"""
Category and tag seeders
"""
from sqlalchemy.orm import Session
from app.models.blog import Category, Tag


def seed_categories(db: Session):
    """Seed categories table"""
    categories_data = [
        # BLOG_POST categories
        {"name": "Technology", "slug": "technology", "type": "BLOG_POST"},
        {"name": "Programming", "slug": "programming", "type": "BLOG_POST"},
        {"name": "Web Development", "slug": "web-development", "type": "BLOG_POST"},
        {"name": "Mobile Development", "slug": "mobile-development", "type": "BLOG_POST"},
        {"name": "DevOps", "slug": "devops", "type": "BLOG_POST"},
        {"name": "Tutorial", "slug": "tutorial", "type": "BLOG_POST"},
        # PROJECT categories
        {"name": "Full Stack", "slug": "full-stack", "type": "PROJECT"},
        {"name": "Frontend", "slug": "frontend", "type": "PROJECT"},
        {"name": "Backend", "slug": "backend", "type": "PROJECT"},
        {"name": "Mobile App", "slug": "mobile-app", "type": "PROJECT"},
        # SKILL categories
        {"name": "Backend", "slug": "backend-skill", "type": "SKILL"},
        {"name": "Frontend", "slug": "frontend-skill", "type": "SKILL"},
        {"name": "DevOps", "slug": "devops-skill", "type": "SKILL"},
        {"name": "Database", "slug": "database", "type": "SKILL"},
    ]
    
    for category_data in categories_data:
        existing_category = db.query(Category).filter(
            Category.slug == category_data["slug"]
        ).first()
        
        if not existing_category:
            category = Category(**category_data)
            db.add(category)
    
    db.commit()
    print("✅ Categories seeded successfully")


def seed_tags(db: Session):
    """Seed tags table"""
    tags_data = [
        {"name": "Python", "slug": "python"},
        {"name": "FastAPI", "slug": "fastapi"},
        {"name": "JavaScript", "slug": "javascript"},
        {"name": "React", "slug": "react"},
        {"name": "Vue.js", "slug": "vuejs"},
        {"name": "Node.js", "slug": "nodejs"},
        {"name": "Docker", "slug": "docker"},
        {"name": "Kubernetes", "slug": "kubernetes"},
        {"name": "AWS", "slug": "aws"},
        {"name": "API", "slug": "api"},
    ]
    
    for tag_data in tags_data:
        existing_tag = db.query(Tag).filter(Tag.slug == tag_data["slug"]).first()
        
        if not existing_tag:
            tag = Tag(**tag_data)
            db.add(tag)
    
    db.commit()
    print("✅ Tags seeded successfully")
