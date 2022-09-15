from fastapi import APIRouter
from .routes.fs import router as fs_router
from db.db import router as db_router
router = APIRouter()
router.include_router(db_router)
router.include_router(fs_router)
