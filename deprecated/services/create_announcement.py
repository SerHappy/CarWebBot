from datetime import datetime
from db.models.announcement import Announcement
from db.models.media import Media
from db.models.tag import Tag
from fastapi import UploadFile
from pathlib import Path
from tortoise.exceptions import IntegrityError

import uuid


async def create_announcement_in_db(
    form,
    media: list[UploadFile],
) -> Announcement:
    try:
        publication = await Announcement.create(
            name=form.name,
            text=form.text,
            price=form.price,
            status=form.status,
            note=form.note if form.note else None,
            publication_date=form.publication_date,
        )

        if media:
            current_file_path = Path(__file__).resolve()
            static_folder_path = current_file_path.parent.parent.parent / "media"

            for media_item in media:
                print(media_item.filename, media_item.content_type, media_item.file)
                # Сохранить медиа в папку static
                unique_id = uuid.uuid4()
                unique_filename = f"{unique_id}-{datetime.now().timestamp()}-{media_item.filename}"

                media_path = static_folder_path / unique_filename
                with open(media_path, "wb") as file:
                    file.write(await media_item.read())

                # Сохранить информацию о медиа в базу данных
                await Media.create(
                    media_type=media_item.content_type.split("/")[0],  # type: ignore
                    url="media/" + unique_filename,
                    publication_id=publication.id,
                )

        if form.tags:
            for tag in form.tags:
                print(tag)
                tag_obj = await Tag.filter(id=tag).first()
                print(tag_obj)
                await publication.tags.add(tag_obj)
        print(publication.tags.all())
        print(publication)
        return publication
    except IntegrityError:
        raise ValueError("Ошибка при сохранении публикации в БД")
