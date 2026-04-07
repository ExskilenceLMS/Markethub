from typing import List, Optional

from sqlalchemy import select

from models import db
from models.category import Category


class CategoryRepository:
    def list_all_ordered(self) -> List[Category]:
        stmt = select(Category).order_by(Category.name)
        return list(db.session.scalars(stmt).all())

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return db.session.get(Category, category_id)

    def get_by_name(self, name: str) -> Optional[Category]:
        stmt = select(Category).where(Category.name == name)
        return db.session.execute(stmt).scalar_one_or_none()

    def create(self, name: str, description: Optional[str]) -> Category:
        c = Category(name=name, description=description or None)
        try:
            db.session.add(c)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return c

    def update(self, category: Category, name: str, description: Optional[str]) -> Category:
        category.name = name
        category.description = description or None
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return category

    def delete(self, category: Category) -> None:
        try:
            db.session.delete(category)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
