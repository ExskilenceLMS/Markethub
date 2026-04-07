from typing import Optional

from sqlalchemy import func, select

from models import db
from models.user import User


class UserRepository:
    def create_user(
        self,
        name: str,
        email: str,
        password_hash: str,
        role: str,
    ) -> User:
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
        )
        try:
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return db.session.execute(stmt).scalar_one_or_none()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return db.session.get(User, user_id)

    def count_all_users(self) -> int:
        n = db.session.scalar(select(func.count(User.id)))
        return int(n or 0)

    def count_users_with_role(self, role: str) -> int:
        n = db.session.scalar(
            select(func.count(User.id)).where(User.role == role),
        )
        return int(n or 0)
