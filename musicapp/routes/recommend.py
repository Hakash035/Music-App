from fastapi import APIRouter
from .. import database, models, schemas

router = APIRouter(
    tags = ["Recommend"]
)

