from sqlalchemy import create_engine, text
from app.core.config import settings

def fix():
    engine = create_engine(str(settings.DATABASE_URL))
    with engine.begin() as conn:
        conn.execute(text("UPDATE alembic_version SET version_num = 'b2c3d4e5f6a7'"))
        print("Fixed alembic version!")

if __name__ == '__main__':
    fix()
