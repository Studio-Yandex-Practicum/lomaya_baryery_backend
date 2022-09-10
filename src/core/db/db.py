from sqlalchemy import create_engine

from src.core.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)
