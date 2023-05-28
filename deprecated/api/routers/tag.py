from core.security import get_current_user
from db.models.tag import Tag
from db.models.user import User
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from tortoise.exceptions import IntegrityError


templates = Jinja2Templates(directory="../templates")

tag_router = APIRouter(prefix="/tag")


@tag_router.post("/add/")
async def create_tag(
    tagName: str = Form(...),
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    try:
        new_tag = await Tag.create(name=tagName)
        return JSONResponse(
            {"status": "success", "message": "Тег успешно создан", "id": new_tag.id, "name": new_tag.name}
        )
    except IntegrityError as e:
        print(e)
        return JSONResponse({"status": "error", "message": "Такой тег уже существует"})
