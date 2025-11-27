"""
Reset the database schema: drop all tables then recreate them.
Assumes DATABASE_URL is set (e.g., in .env or environment).
"""
from app.db import Base, engine


def main():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    print("Done.")


if __name__ == "__main__":
    main()
