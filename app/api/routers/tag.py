from db.models.tag import Tag
from fastapi import APIRouter
from fastapi import Form
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from tortoise.exceptions import IntegrityError


templates = Jinja2Templates(directory="../templates")

tag_router = APIRouter(prefix="/tag")


@tag_router.post("/add/")
async def create_tag(
    tagName: str = Form(...),
) -> JSONResponse:
    try:
        new_tag = await Tag.create(name=tagName)
        return JSONResponse(
            {"status": "success", "message": "Тег успешно создан", "id": new_tag.id, "name": new_tag.name}
        )
    except IntegrityError as e:
        print(e)
        return JSONResponse({"status": "error", "message": "Такой тег уже существует"})
