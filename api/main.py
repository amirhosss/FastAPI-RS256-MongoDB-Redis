from fastapi import APIRouter

from api.endpoints import users, auth

router = APIRouter(
    prefix='/api'
)

router.include_router(users.router)
router.include_router(auth.router)