window.updateStatuses = async function () {
    console.log("Начинаем обновление статусов");

    const rows = $("#announcementsTable .announcement-row");
    console.log(`Обработка ${rows.length} строк`);
    for (let row of rows) {
        const $row = $(row);
        const announcementId = $row.data("announcement-id");
        console.log(`Обработка объявления с ID: ${announcementId}`);

        try {
            console.log(`Отправка запроса на получение статуса для объявления с ID: ${announcementId}`);
            const data = await $.ajax({
                type: "GET",
                url: `/announcements/status/${announcementId}/`,
                dataType: "json",
            });

            let status = data.status.toLowerCase();
            console.log(`Получен статус для объявления ${announcementId}: ${status}`);
            let published_message_link = data.published_message_link;

            console.log(`Поиск элементов на странице для объявления с ID: ${announcementId}`);
            const copyButton = $row.find(".copy-button");
            const takeoffButton = $row.find(".takeoff-button");
            const statusIcon = $row.find(".status-icon");
            const statusText = $row.find(`#status_text_${announcementId}`);

            console.log(`Обработка статуса для объявления с ID: ${announcementId}`);
            console.log(`Текущая ссылка на сообщение для объявления с ID: ${announcementId}: ${$row.attr("data-published-message-link")}`);
            if (status.startsWith("опубликовано")) {
                console.log(`Статус опубликовано для объявления с ID: ${announcementId}`);
                copyButton.show();
                takeoffButton.show();
                statusIcon.removeClass('status-awaiting status-removed').addClass('status-published');
                $row.removeAttr("data-published-message-link");
                $row.attr("data-published-message-link", published_message_link);
                console.log($row);
                console.log(`Новая ссылка на сообщение для объявления с ID: ${announcementId}: ${published_message_link}`);
            } else if (status.startsWith("ожидает публикации")) {
                console.log(`Статус ожидает публикации для объявления с ID: ${announcementId}`);
                copyButton.hide();
                takeoffButton.show();
                statusIcon.removeClass('status-published status-removed').addClass('status-awaiting');
                console.log(`Удалена ссылка на сообщение для объявления с ID: ${announcementId}`);
                $row.removeAttr("data-published-message-link");
            } else if (status.startsWith("снято с публикации") || status.startsWith("не было опубликовано")) {
                console.log(`Статус снято с публикации или не опубликовано для объявления с ID: ${announcementId}`);
                copyButton.hide();
                takeoffButton.hide();
                statusIcon.removeClass('status-published status-awaiting').addClass('status-removed');
                $row.addClass('inactive-row');
                console.log(`Удалена ссылка на сообщение для объявления с ID: ${announcementId}`);
                $row.removeAttr("data-published-message-link");
            } else {
                $row.removeClass('inactive-row');
            }

            if (!status.startsWith("снято с публикации") && !status.startsWith("не было опубликовано")) {
                console.log(`Статус не снято с публикации и не не опубликовано для объявления с ID: ${announcementId}`);
                $row.removeClass('table-secondary');
            }

            const publicationDate = formatDate(new Date(data.publication_date));
            if (["опубликовано", "ожидает публикации"].includes(status)) {
                console.log(`Добавление времени публикации к статусу для объявления с ID: ${announcementId}`);
                status += ` ${publicationDate}`;
            }
            const unpublishedDate = formatDate(new Date(data.unpublished_date));
            console.log()
            console.log(`Время снятия с публикации для объявления с ID: ${announcementId}: ${unpublishedDate}`);
            if (status.startsWith("снято с публикации")) {
                console.log(`Добавление времени снятия с публикации к статусу для объявления с ID: ${announcementId}`);
                status += ` ${unpublishedDate}`;
            }

            console.log(`Обновление текста статуса на странице для объявления с ID: ${announcementId}`);
            statusText.text(status);
        } catch (error) {
            console.error(`Ошибка при обновлении статуса для объявления ${announcementId}:`, error);
        }
    }

    console.log("Завершено обновление статусов");
}

function formatDate(date) {
    console.log("Форматирование даты");
    const pad = (n) => (n < 10 ? '0' : '') + n;
    const day = pad(date.getDate());
    const month = pad(date.getMonth() + 1);
    const year = date.getFullYear();
    const hours = date.getHours();
    const minutes = pad(date.getMinutes());
    return `${day}.${month}.${year} в ${hours}:${minutes}`;
}
