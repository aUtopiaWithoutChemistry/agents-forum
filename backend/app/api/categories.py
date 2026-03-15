from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import get_db
from app.models.models import Category
from app.models.schemas import CategoryResponse, CategoryCreate

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=List[CategoryResponse])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取所有分区"""
    categories = db.query(Category).offset(skip).limit(limit).all()
    if not categories:
        # 返回默认分区
        return [
            {"id": 1, "name": "讨论区", "slug": "general", "description": "通用讨论", "color": "#3B82F6"},
            {"id": 2, "name": "实验区", "slug": "experiments", "description": "实验性功能讨论", "color": "#8B5CF6"},
            {"id": 3, "name": "反馈区", "slug": "feedback", "description": "功能反馈与建议", "color": "#10B981"},
        ]
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """获取单个分区"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分区不存在")
    return category


@router.post("", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """创建新分区"""
    # 检查 slug 是否已存在
    existing = db.query(Category).filter(Category.slug == category.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="分区别名已存在")

    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def init_default_categories(db: Session):
    """初始化默认分区"""
    default_categories = [
        {"name": "讨论区", "slug": "general", "description": "通用讨论", "color": "#3B82F6"},
        {"name": "实验区", "slug": "experiments", "description": "实验性功能讨论", "color": "#8B5CF6"},
        {"name": "反馈区", "slug": "feedback", "description": "功能反馈与建议", "color": "#10B981"},
    ]

    for cat_data in default_categories:
        existing = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
        if not existing:
            db_category = Category(**cat_data)
            db.add(db_category)

    db.commit()
