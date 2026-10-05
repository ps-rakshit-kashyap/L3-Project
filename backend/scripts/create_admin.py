import argparse
import sys
import uuid
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.models.user import User, UserRole


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote an initial Admin user for TalentForge.")
    parser.add_argument("--email", required=True, help="User email address")
    parser.add_argument("--name", default="System Administrator", help="User full name")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == args.email.strip()).first()
        if user:
            old_role = user.role
            user.role = UserRole.ADMIN.value
            db.commit()
            print(f"Updated existing user '{user.email}' from role '{old_role}' to '{UserRole.ADMIN.value}' (User ID: {user.id})")
        else:
            new_admin = User(
                id=uuid.uuid4(),
                name=args.name.strip(),
                email=args.email.strip(),
                role=UserRole.ADMIN.value,
            )
            db.add(new_admin)
            db.commit()
            print(f"Created new ADMIN user '{new_admin.email}' (User ID: {new_admin.id})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
