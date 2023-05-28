from core.security import get_current_user
from datetime import datetime
from db.models import Tag
from db.models.announcement import Announcement
from db.models.user import User
from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import Form
from fastapi import Query
from fastapi import Request
from fastapi import UploadFile
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseConfig
from pydantic import BaseModel
from services.create_announcement import create_announcement_in_db
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import Optional

import json
import pytz


templates = Jinja2Templates(directory="../templates")

announcement_router = APIRouter(prefix="/announcement")

Announcement_Pydantic = pydantic_model_creator(Announcement, name="Announcement")


class MediaPydantic(BaseModel):
    id: int
    media_type: str
    url: str
    publication_id: int

    class Config(BaseConfig):
        orm_mode = True


class AnnouncementPydantic(BaseModel):
    id: int | None = None
    name: str | None = None
    text: str | None = None
    price: str | None = None
    status: str | None = None
    tags: Optional[list[str | dict]] = None
    media: Optional[list[MediaPydantic]] = None
    note: Optional[str] = None
    publication_date: str | datetime | None = None
    timezone: str = "UTC"
    is_published: bool = False
    is_active: bool = True

    def json(self):
        return json.dumps(self.dict(), default=lambda x: x.isoformat() if isinstance(x, datetime) else str(x))

    class Config(BaseConfig):
        orm_mode = True


def parse_form(
    name: str = Form(...),
    text: str = Form(...),
    price: str = Form(...),
    status: str = Form(...),
    tags: Optional[list[str | dict]] = Form(None),
    note: Optional[str] = Form(None),
    publication_date: str | datetime = Form(...),
    timezone: str = Form(None),
) -> AnnouncementPydantic:
    return AnnouncementPydantic(
        name=name,
        text=text,
        price=price,
        status=status,
        tags=tags,
        note=note,
        publication_date=publication_date,
        timezone=timezone,
    )


@announcement_router.get("/", response_class=HTMLResponse)
async def get_announcements(
    ids: list[int] = Query(None),
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    if ids:
        announcements = await Announcement.filter(id__in=ids).all().values()
    else:
        announcements = await Announcement.all().values()
    return JSONResponse([AnnouncementPydantic.parse_obj(a).json() for a in announcements])


@announcement_router.get("/add/", response_class=HTMLResponse)
async def create_announcement_form(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> Response:
    tags = await Tag.all()
    return templates.TemplateResponse(
        "announcement/announcement_form.html",
        {
            "request": request,
            "tags": tags,
        },
    )


@announcement_router.post("/add/", response_class=HTMLResponse)
async def create_announcement(
    request: Request,
    form: AnnouncementPydantic = Depends(parse_form),
    media: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
) -> Response:
    try:
        user_date = datetime.strptime(form.publication_date, "%d.%m.%Y %H:%M")  # type: ignore
        user_timezone = pytz.timezone(form.timezone)
        user_date = user_timezone.localize(user_date)

        utc_date = user_date.astimezone(pytz.UTC)

        form.publication_date = utc_date
        form.publication_date = datetime.strptime(str(form.publication_date), "%Y-%m-%d %H:%M:%S%z")
        await create_announcement_in_db(form, media)
        tags = await Tag.all()
        return templates.TemplateResponse(
            "announcement/announcement_form.html",
            {
                "request": request,
                "tags": tags,
                "announcement": None,
            },
        )
    except ValueError as e:
        print(e)
        return JSONResponse({"error": str(e)}, status_code=400)


@announcement_router.get("/edit/{announcement_id}/", response_class=HTMLResponse)
async def edit_announcement_form(
    request: Request,
    announcement_id: int,
    current_user: User = Depends(get_current_user),
) -> Response:
    tags = await Tag.all()
    announcement = await Announcement.get(id=announcement_id)

    # Получить все связанные Media объекты
    media_objects = await announcement.media.all()
    tags_objects = await announcement.tags.all()
    # Преобразовать каждый объект Media в словарь и добавить их в список
    media = [media.__dict__ for media in media_objects]
    tags = [tag.__dict__ for tag in tags_objects]
    # Добавить список словарей media в словарь announcement
    announcement.__dict__["media"] = media
    announcement.__dict__["tags"] = tags
    announcement_json = AnnouncementPydantic(**announcement.__dict__).json()

    return templates.TemplateResponse(
        "announcement/announcement_form.html",
        {
            "request": request,
            "tags": tags,
            "announcement": announcement_json,
        },
    )
