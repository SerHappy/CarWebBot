from datetime import datetime
from db.models import Tag
from db.models.announcement import Announcement
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
from typing import Optional

import json
import pytz


templates = Jinja2Templates(directory="../templates")

announcement_router = APIRouter(prefix="/announcement")


class AnnouncementPydantic(BaseModel):
    id: int | None = None
    name: str | None = None
    text: str | None = None
    price: str | None = None
    status: str | None = None
    tags: Optional[list[str]] = None
    note: Optional[str] = None
    publication_date: str | datetime | None = None
    timezone: str = "UTC"
    is_published: bool = False
    is_active: bool = True

    def json(self):
        return json.dumps(self.dict(), default=str)

    class Config(BaseConfig):
        orm_mode = True


def parse_form(
    name: str = Form(...),
    text: str = Form(...),
    price: str = Form(...),
    status: str = Form(...),
    tags: Optional[list[str]] = Form(None),
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
async def get_announcements(ids: list[int] = Query(None)) -> JSONResponse:
    if ids:
        announcements = await Announcement.filter(id__in=ids).all().values()
    else:
        announcements = await Announcement.all().values()
    return JSONResponse([AnnouncementPydantic.parse_obj(a).json() for a in announcements])


@announcement_router.get("/add/", response_class=HTMLResponse)
async def create_announcement_form(request: Request) -> Response:
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
) -> Response:
    print(await request.form())
    try:
        # Получить дату и время и часовой пояс от пользователя
        # This code block is converting the publication date and timezone submitted by the user in the form into a UTC datetime
        # object that can be saved in the database.
        user_date = datetime.strptime(form.publication_date, "%d.%m.%Y %H:%M")  # type: ignore
        user_timezone = pytz.timezone(form.timezone)
        # Сделать дату и время "сознательными" относительно часового пояса пользователя
        user_date = user_timezone.localize(user_date)

        # Преобразовать дату и время в UTC
        utc_date = user_date.astimezone(pytz.UTC)

        # Теперь вы можете сохранить utc_date в базе данных
        form.publication_date = utc_date
        form.publication_date = datetime.strptime(str(form.publication_date), "%Y-%m-%d %H:%M:%S%z")
        await create_announcement_in_db(form, media)
        tags = await Tag.all()
        return templates.TemplateResponse(
            "announcement/announcement_form.html",
            {
                "request": request,
                "tags": tags,
            },
        )
    except ValueError as e:
        print(e)
        return JSONResponse({"error": str(e)}, status_code=400)


@announcement_router.get("/edit/{announcement_id}/", response_class=HTMLResponse)
async def edit_announcement_form(request: Request, announcement_id: int) -> Response:
    tags = await Tag.all()
    announcement = await Announcement.get(id=announcement_id)
    return templates.TemplateResponse(
        "announcement_form.html",
        {
            "request": request,
            "tags": tags,
            "announcement": announcement,
        },
    )
