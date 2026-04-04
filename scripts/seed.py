"""Create demo data for local development.

Run: python3 scripts/seed.py

Idempotent — safe to run multiple times. Checks for existing data before creating.
"""

import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models import User

DEMO_EMAIL = "demo@superstories.com"


def seed():
    """Create a demo user if one does not already exist."""
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == DEMO_EMAIL).first()

        if existing_user:
            print(f"Demo user already exists: {DEMO_EMAIL} (id={existing_user.id})")
            return

        demo_user = User(email=DEMO_EMAIL)
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

        print(f"Created demo user: {DEMO_EMAIL} (id={demo_user.id})")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
