from sqlalchemy import select

from app.auth.security import get_password_hash
from app.database import SessionLocal
from app.models.user import User


DEV_USERS = [
    {
        "email": "admin@example.com",
        "full_name": "Development Admin",
        "password": "AdminPassword123!",
        "role": "admin",
    },
    {
        "email": "tech@example.com",
        "full_name": "Development Tech",
        "password": "StrongPassword123!",
        "role": "tech",
    },
]


def main() -> None:
    db = SessionLocal()

    try:
        for dev_user in DEV_USERS:
            existing_user = db.scalar(
                select(User).where(User.email == dev_user["email"])
            )

            if existing_user is None:
                user = User(
                    email=dev_user["email"],
                    full_name=dev_user["full_name"],
                    hashed_password=get_password_hash(dev_user["password"]),
                    role=dev_user["role"],
                    is_active=True,
                )
                db.add(user)
                print(f"Created {dev_user['email']}")
            else:
                existing_user.full_name = dev_user["full_name"]
                existing_user.hashed_password = get_password_hash(
                    dev_user["password"]
                )
                existing_user.role = dev_user["role"]
                existing_user.is_active = True
                print(f"Updated {dev_user['email']}")

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    main()
