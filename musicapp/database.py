from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Annotated
from fastapi import Depends
from elasticsearch import Elasticsearch

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost:5432/musicApp"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

#ElasticSearch Config
ELASTICSEARCH_URL = "https://localhost:9200"
es = Elasticsearch(hosts=ELASTICSEARCH_URL, basic_auth=("elastic", "c9EzKcChn*OWBX86a0ZD"), verify_certs=False)