from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .freelancers import router as freelancers_router
from .newsrooms import router as newsrooms_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(freelancers_router, prefix="/freelancers", tags=["Freelancers"])
api_router.include_router(newsrooms_router, prefix="/newsrooms", tags=["Newsrooms"])
