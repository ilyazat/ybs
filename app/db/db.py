from typing import List
import logging
import databases
import sqlalchemy
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

# SQLAlchemy specific code, as with any other app
DATABASE_URL = "postgresql://postgres:zzz@localhost:5432/postgres"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

items_table = sqlalchemy.Table(
    "items",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String(50), primary_key=True, nullable=False),
    sqlalchemy.Column("url", sqlalchemy.String(255)),
    sqlalchemy.Column("date", sqlalchemy.String(50), nullable=False),
    sqlalchemy.Column("parent_id", sqlalchemy.String(50)),
    sqlalchemy.Column("item_type", sqlalchemy.String(50), nullable=False),
    sqlalchemy.Column("size", sqlalchemy.Integer())
)

items_history = sqlalchemy.Table(
    "history",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String(50), nullable=False),
    sqlalchemy.Column("url", sqlalchemy.String(255)),
    sqlalchemy.Column("parent_id", sqlalchemy.String(50)),
    sqlalchemy.Column("item_type", sqlalchemy.String(10), nullable=False),
    sqlalchemy.Column("size", sqlalchemy.Integer()),
    sqlalchemy.Column("date", sqlalchemy.String(50))
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)

router = APIRouter()
