from api.routers.announcement import announcement_router
from api.routers.auth import auth_router
from api.routers.index import index_router
from api.routers.tag import tag_router
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise

app = FastAPI()
app.include_router(index_router)
app.include_router(announcement_router)
app.include_router(tag_router)
app.include_router(auth_router)
app.mount("/static", StaticFiles(directory="../static"), name="static")
app.mount("/media", StaticFiles(directory="../media"), name="media")

register_tortoise(
    app,
    db_url="mysql://root:root@localhost:3306/cars",
    modules={"models": ["db.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)