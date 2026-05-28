"""
Skill seeder
"""
from sqlalchemy.orm import Session
from app.models.other import Skill
from app.models.blog import Category


def seed_skills(db: Session):
    """Seed skills table — uses category_id FK to categories table."""
    # Look up categories by slug (seeded earlier by category_tag_seeder)
    categories = {c.slug: c for c in db.query(Category).filter(Category.type == 'SKILL').all()}

    skills_data = [
        {"name": "Python", "category_slug": "backend-skill", "level": 90, "icon_url": "https://example.com/icons/python.svg", "sort_order": 1},
        {"name": "FastAPI", "category_slug": "backend-skill", "level": 85, "icon_url": "https://example.com/icons/fastapi.svg", "sort_order": 2},
        {"name": "Django", "category_slug": "backend-skill", "level": 80, "icon_url": "https://example.com/icons/django.svg", "sort_order": 3},
        {"name": "JavaScript", "category_slug": "frontend-skill", "level": 85, "icon_url": "https://example.com/icons/javascript.svg", "sort_order": 4},
        {"name": "TypeScript", "category_slug": "frontend-skill", "level": 80, "icon_url": "https://example.com/icons/typescript.svg", "sort_order": 5},
        {"name": "React", "category_slug": "frontend-skill", "level": 85, "icon_url": "https://example.com/icons/react.svg", "sort_order": 6},
        {"name": "Vue.js", "category_slug": "frontend-skill", "level": 75, "icon_url": "https://example.com/icons/vuejs.svg", "sort_order": 7},
        {"name": "Docker", "category_slug": "devops-skill", "level": 80, "icon_url": "https://example.com/icons/docker.svg", "sort_order": 8},
        {"name": "Kubernetes", "category_slug": "devops-skill", "level": 70, "icon_url": "https://example.com/icons/kubernetes.svg", "sort_order": 9},
        {"name": "PostgreSQL", "category_slug": "database", "level": 85, "icon_url": "https://example.com/icons/postgresql.svg", "sort_order": 10},
        {"name": "MySQL", "category_slug": "database", "level": 85, "icon_url": "https://example.com/icons/mysql.svg", "sort_order": 11},
        {"name": "MongoDB", "category_slug": "database", "level": 75, "icon_url": "https://example.com/icons/mongodb.svg", "sort_order": 12},
    ]
    
    for skill_data in skills_data:
        category_slug = skill_data.pop("category_slug")
        category = categories.get(category_slug)

        existing_skill = db.query(Skill).filter(Skill.name == skill_data["name"]).first()
        
        if not existing_skill:
            skill = Skill(category_id=category.id if category else None, **skill_data)
            db.add(skill)
    
    db.commit()
    print("✅ Skills seeded successfully")
