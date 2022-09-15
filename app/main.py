from fastapi import FastAPI
import uvicorn
from api.routes.fs import router as fs_router
from db.db import database
import logging


app = FastAPI()
app.include_router(fs_router)
