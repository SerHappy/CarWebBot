from ..models import Tag
from apps.announcement.models import Announcement
from apps.bot.views import delete_announcement_from_subchannel
from apps.bot.views import edit_announcement_in_channel
from dataclasses import dataclass
from django.core.paginator import EmptyPage
from django.core.paginator import InvalidPage
from django.core.paginator import Page
from django.core.paginator import PageNotAnInteger
from django.core.paginator import Paginator
from django.db.models import QuerySet
from loguru import logger


@dataclass
class TagData:
    """
    Дата-класс для хранения данных тега.

    Attributes:
        name (str): Название тега.
        tag_type (str): Тип тега.
        channel_id (int): ID канала, к которому привязан тег.
        tag_id (int, optional): ID тега, если он уже создан.
    """

    name: str
    tag_type: str
    channel_id: int | None = None
    tag_id: int | None = None


@dataclass
class DeleteResult:
    """
    Класс, представляющий результат удаления.

    Хранит состояние успешности удаления и возможное сообщение об ошибке.

    Attributes:
        success (bool): Успешность удаления.
        error_message (str, optional): Сообщение об ошибке, если удаление не удалось.
    """

    def __init__(self, success: bool, error_message: str | None = None) -> None:
        """
        Инициализирует объект результата удаления.

        Args:
            success (bool): Успешность удаления.
            error_message (str, optional): Сообщение об ошибке, если есть.
        """
        self.success = success
        self.error_message = error_message

    def is_success(self) -> bool:
        """
        Проверяет успешность удаления.

        Returns:
            bool: True, если удаление успешно, иначе False.
        """
        return self.success

    @staticmethod
    def successful() -> "DeleteResult":
        """
        Создает объект результата удаления с состоянием успеха.

        Returns:
            DeleteResult: Объект с успешным результатом удаления.
        """
        return DeleteResult(True)

    @staticmethod
    def failure(message: str) -> "DeleteResult":
        """
        Создает объект результата удаления с состоянием неудачи.

        Args:
            message (str): Сообщение об ошибке.

        Returns:
            DeleteResult: Объект с неудачным результатом удаления и сообщением об ошибке.
        """
        return DeleteResult(False, message)


class ValidationResult:
    """
    Класс, представляющий результат валидации.

    Хранит состояние успешности валидации и возможное сообщение об ошибке.

    Attributes:
        success (bool): Успешность валидации.
        error_message (str, optional): Сообщение об ошибке, если валидация не пройдена.
    """

    def __init__(self, success: bool, error_message: str | None = None) -> None:
        """
        Инициализирует объект результата валидации.

        Args:
            success (bool): Успешность валидации.
            error_message (str, optional): Сообщение об ошибке, если есть.
        """
        self.success = success
        self.error_message = error_message

    def is_success(self) -> bool:
        """
        Проверяет успешность валидации.

        Returns:
            bool: True, если валидация успешна, иначе False.
        """
        return self.success

    @staticmethod
    def successful() -> "ValidationResult":
        """
        Создает объект результата валидации с состоянием успеха.

        Returns:
            ValidationResult: Объект с успешным результатом валидации.
        """
        return ValidationResult(True)

    @staticmethod
    def failure(message: str) -> "ValidationResult":
        """
        Создает объект результата валидации с состоянием неудачи.

        Args:
            message (str): Сообщение об ошибке.

        Returns:
            ValidationResult: Объект с неудачным результатом валидации и сообщением об ошибке.
        """
        return ValidationResult(False, message)


class TagValidator:
    """
    Класс для валидации тегов при создании, обновлении и проверке существования.

    Метод `validate` используется для валидации данных тега при создании или обновлении.
    Метод `check_is_tag_name_taken` используется для проверки, существует ли тег с указанным именем в базе данных.

    Пример использования для валидации создания или обновления тега:
        ```
        validator = TagValidator()
        tag_data = TagData(name="example", tag_type="visible", channel_id=123)
        result = validator.validate(tag_data)
        if result.is_success():
            # Продолжить обработку
        else:
            print(result.error_message)
        ```
    """

    def check_is_tag_name_taken(self, tag_name: str, tag_id: int | None = None) -> bool:
        """
        Проверяет, существует ли тег с указанным именем в базе данных.

        Исключает тег с переданным ID из проверки.

        Args:
            tag_name (str): Имя тега для проверки.
            tag_id (int, optional): ID тега, который нужно исключить из проверки.

        Returns:
            bool: True, если имя уже занято, иначе False.
        """
        query = Tag.objects.filter(name=tag_name)
        if tag_id:
            query = query.exclude(id=tag_id)
        return query.exists()

    def validate(self, tag_to_validate: TagData) -> ValidationResult:
        """
        Валидирует данные тега для создания или обновления.

        Args:
            tag_to_validate (TagData): Объект данных тега, содержащий имя, тип, channel_id и возможно, ID тега.

        Returns:
            ValidationResult: Объект с результатом валидации.
        """
        validation_result: ValidationResult = self._validate_common(tag_to_validate)
        if not validation_result.is_success():
            return validation_result
        return self._validate_name_existence(tag_to_validate)

    def _validate_common(self, tag_to_validate: TagData) -> ValidationResult:
        """
        Производит общую валидацию данных тега.

        Args:
            tag_to_validate (TagData): Объект данных тега, содержащий имя, тип, channel_id и возможно, ID тега.

        Returns:
            ValidationResult: Объект с результатом валидации.
        """
        max_length = Tag._meta.get_field("name").max_length
        if tag_to_validate.name is None:
            return ValidationResult.failure("Название тега не указано")
        if tag_to_validate.tag_type is None:
            return ValidationResult.failure("Тип тега не указан")
        if tag_to_validate.tag_type not in Tag.TagType.values:
            return ValidationResult.failure("Неверный тип тега")
        if len(tag_to_validate.name) < 1:
            return ValidationResult.failure("Название тега слишком короткое")
        if len(tag_to_validate.name) > max_length:
            return ValidationResult.failure("Название тега слишком длинное")
        return ValidationResult.successful()

    def _validate_name_existence(self, tag_to_validate: TagData) -> ValidationResult:
        """
        Валидирует имя тега на уникальность. Если `tag_to_validate` содержит ID тега, то исключает его.

        Args:
            tag_to_validate (TagData): Объект данных тега, содержащий имя, тип, channel_id и возможно, ID тега.

        Returns:
            ValidationResult: Объект с результатом валидации.
        """
        if self._check_if_tag_is_already_created(tag_to_validate):
            return ValidationResult.failure("Тег с таким именем уже существует")
        return ValidationResult.successful()

    def _check_if_tag_is_already_created(self, tag_to_validate: TagData) -> bool:
        """
        Проверяет, существует ли тег с таким же именем. Если `tag_to_validate` содержит ID тега, то исключает его.

        Args:
            tag_to_validate (TagData): Объект данных тега, содержащий имя, тип, channel_id и возможно, ID тега.

        Returns:
            ValidationResult: True, если тег с таким именем уже существует, иначе False.
        """
        if tag_to_validate.tag_id:
            return Tag.objects.filter(name__iexact=tag_to_validate.name).exclude(pk=tag_to_validate.tag_id).exists()
        return Tag.objects.filter(name__iexact=tag_to_validate.name).exists()


class TagService:
    """Класс для работы с тегами."""

    def _fetch_all_tags_from_db(self) -> QuerySet[Tag]:
        """
        Извлекает все теги из базы данных.

        Returns:
            QuerySet[Tag]: QuerySet со всеми тегами.
        """
        return Tag.objects.all()

    def fetch_tag_from_db(self, pk: int) -> Tag | None:
        """
        Пытается извлечь тег из базы данных по его ID.

        Args:
            pk (int): ID тега.

        Returns:
            Tag | None: Объект тега, если тег с таким ID существует, иначе None.
        """
        try:
            return Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            return None

    def get_tags_for_display(self, name_filter: str | None = None, page: int = 1, page_size: int = 10) -> Page:
        """
        Получает список тегов для отображения, применяя фильтрацию и пагинацию.

        Args:
            name_filter (str | None): Имя для фильтрации.

            page (int): Номер страницы. По умолчанию 1.

            page_size (int): Количество тегов на странице. По умолчанию 10.

        Returns:
            Page: Объект Page, содержащий теги для текущей страницы.
        """
        filtered_tags = self._filter_tags_by_name(name_filter)
        return self._paginate_tags(filtered_tags, page, page_size)

    def _filter_tags_by_name(self, name: str | None) -> QuerySet[Tag]:
        """
        Фильтрует теги, имя которых содержит переданное `name`. Регистр символов не учитывается.

        Args:
            name (str): Имя для фильтрации.

        Returns:
            QuerySet[Tag]: QuerySet с тегами, соответствующими критерию фильтрации.
        """
        if name is None:
            return self._fetch_all_tags_from_db()

        return Tag.objects.filter(name__icontains=name)

    def _paginate_tags(self, tags: QuerySet[Tag], page_number: int, page_size: int) -> Page:
        """
        Пагинирует список тегов.

        Args:
            tags (QuerySet[Tag]): Список тегов для пагинации.

            page_number (int): Номер страницы.

            page_size (int): Количество тегов на странице.

        Returns:
            Page: Пагинированный список тегов.
        """
        paginator = Paginator(tags, page_size)

        try:
            return paginator.page(page_number)
        except PageNotAnInteger:
            logger.warning(f"Page {page_number} of tags was not an integer. Defaulting to page 1.")
            return paginator.page(1)
        except EmptyPage:
            logger.warning(f"Page {page_number} of tags was empty. Defaulting to page 1.")
            return paginator.page(1)
        except InvalidPage:
            logger.warning(f"Page {page_number} of tags was invalid. Defaulting to page 1.")
            return paginator.page(1)

    def create_tag(self, tag_to_create: TagData) -> ValidationResult:
        """
        Создаёт новый тег на основе данных, предоставленных в объекте `tag_to_create`.

        Метод вначале валидирует входные данные с использованием `TagValidator`.
        Если валидация проходит успешно, метод создаёт новый тег в базе данных.

        Args:
            tag_to_create (TagData): Объект, содержащий данные для создания нового тега, включая имя тега,
            тип и ID канала.

        Returns:
            ValidationResult: Объект с результатом валидации, содержащий информацию об успехе или ошибке.
        """
        validator = TagValidator()
        validation_result: ValidationResult = validator.validate(tag_to_create)
        if not validation_result.is_success():
            return validation_result

        try:
            Tag.objects.create(
                name=tag_to_create.name,
                type=tag_to_create.tag_type,
                channel_id=tag_to_create.channel_id,
            )
        except Exception as e:
            logger.critical(f"Got highly unexpected exception while creating tag: {e}. Fix it ASAP!")
            return ValidationResult.failure(str(e))
        return validation_result

    def update_tag(self, tag_to_update: TagData) -> ValidationResult:
        """
        Обновляет тег на основе данных, предоставленных в объекте `tag_to_update`.

        Метод вначале валидирует входные данные с использованием `TagValidator`.
        Если валидация проходит успешно, метод обновляет тег в базе данных.

        Args:
            tag_to_update (TagData): Объект, содержащий данные для обновления тега, включая имя тега, тип,
            ID канала и ID тега.

        Returns:
            ValidationResult: Объект с результатом валидации, содержащий информацию об успехе или ошибке.
        """
        validator = TagValidator()
        validation_result: ValidationResult = validator.validate(tag_to_update)
        if not validation_result.is_success():
            return validation_result

        old_channel_id = None

        try:
            if tag_to_update.tag_id is None:
                return ValidationResult.failure("Tag ID is required to update a tag.")
            tag = self.fetch_tag_from_db(tag_to_update.tag_id)
            if tag is None:
                return ValidationResult.failure(f"Tag with ID {tag_to_update.tag_id} does not exist.")

            old_channel_id = tag.channel_id

            tag.name = tag_to_update.name
            tag.type = tag_to_update.tag_type
            if tag_to_update.channel_id is not None:
                tag.channel_id = tag_to_update.channel_id
            tag.save()
        except Exception as e:
            logger.critical(f"Got highly unexpected exception while updating tag: {e}. Fix it ASAP!")
            return ValidationResult.failure(str(e))

        # TODO: Метод слишком много делает. Нужно разбить на несколько методов.
        # TODO: Не соответствует SRP.
        # TODO: Логика редактирования объявлений должна быть в другом месте.
        announcements = tag.announcements.filter(processing_status=Announcement.ProcessingStatus.PUBLISHED).order_by(
            "publication_date"
        )

        for announcement in announcements:
            current_tags = announcement.tags.all()

            old_tags = {t: old_channel_id if t == tag else t.channel_id for t in current_tags}

            edit_announcement_in_channel(announcement, old_tags)
        return validation_result

    # TODO: Метод слишком много делает. Нужно разбить на несколько методов.
    # TODO: Не соответствует SRP.
    # TODO: Логика удаления объявлений должна быть в другом месте.
    def delete_tag(self, tag_id: int) -> DeleteResult:
        """
        Удаляет тег из базы данных. Так же удаляет все объявления, связанные с этим тегом.

        Args:
            tag_id (int): ID тега.

        Returns:
            DeleteResult: Объект с результатом удаления, содержащий информацию об успехе или ошибке.
        """
        tag_to_delete = self.fetch_tag_from_db(tag_id)
        if tag_to_delete is None:
            return DeleteResult.failure("Тег для удаления не найден")

        tag_announcements = list(tag_to_delete.announcements.all())
        old_channel_id = tag_to_delete.channel_id
        tag_name = tag_to_delete.name

        for announcement in tag_announcements:
            delete_announcement_from_subchannel(announcement, tag_to_delete)

        tag_to_delete.delete()

        for announcement in tag_announcements:
            announcement.refresh_from_db()
            edit_announcement_in_channel(announcement, {tag_name: old_channel_id})
        return DeleteResult.successful()
