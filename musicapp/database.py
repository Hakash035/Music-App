from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Annotated
from fastapi import Depends
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Create a SQLAlchemy engine
engine = create_engine(os.environ.get("SQLALCHEMY_DATABASE_URL"))

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

def get_db():

    """
    Dependency function to provide a database session.

    Returns:
        Session: The SQLAlchemy database session.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Annotated dependency for FastAPI to inject the database session
db_dependency = Annotated[Session, Depends(get_db)]

# Elasticsearch Configuration
ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL")
ELASTICSEARCH_USER = os.environ.get("ELASTICSEARCH_USER")
ELASTICSEARCH_PASSWORD = os.environ.get("ELASTICSEARCH_PASSWORD")

# Create an Elasticsearch instance
es = Elasticsearch(
    hosts=ELASTICSEARCH_URL,
    basic_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
    verify_certs=True
)
