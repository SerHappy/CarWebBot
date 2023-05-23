from db.models import Announcement
from db.models import Tag
from fastapi import APIRouter
from fastapi import Query
from fastapi import Request
from fastapi import Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from math import ceil


index_router = APIRouter()
templates = Jinja2Templates(directory="../templates")


@index_router.get("/", response_class=HTMLResponse)
async def main_page(
    request: Request,
    page: int = 1,
    per_page: int = 2,
    name_filter: str = Query(None),
    tag_filter: str = Query(None),
) -> Response:
    query = Announcement.all().prefetch_related("tags", "media")
    if name_filter:
        print(name_filter)
        query = query.filter(name__istartswith=name_filter)
        for pub in await query.all():
            print(pub.name)

    if tag_filter:
        query = query.filter(tags__name__icontains=tag_filter)

    total_announcements = await query.count()
    total_pages = ceil(total_announcements / per_page)

    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    announcements = (await query)[start_index:end_index]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "announcements": announcements,
            "current_page": page,
            "total_pages": total_pages,
        },
    )
