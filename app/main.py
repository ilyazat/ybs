from fastapi import FastAPI
from app.api.routes.fs import router as fs_router

app = FastAPI()
app.include_router(fs_router)
