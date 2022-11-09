from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Setting up the database connection and creating the session as well as the engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./addressbook.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get the database session using the sessionmaker
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
