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

            console.log(`Поиск элементов на странице для объявления с ID: ${announcementId}`);
            const copyButton = $row.find(".copy-button");
            const takeoffButton = $row.find(".takeoff-button");
            const statusIcon = $row.find(".status-icon");
            const statusText = $row.find(`#status_text_${announcementId}`);

            console.log(`Обработка статуса для объявления с ID: ${announcementId}`);
            if (status.startsWith("опубликовано")) {
                console.log(`Статус опубликовано для объявления с ID: ${announcementId}`);
                copyButton.show();
                takeoffButton.show();
                statusIcon.removeClass('status-awaiting status-removed').addClass('status-published');
            } else if (status.startsWith("ожидает публикации")) {
                console.log(`Статус ожидает публикации для объявления с ID: ${announcementId}`);
                takeoffButton.show();
                statusIcon.removeClass('status-published status-removed').addClass('status-awaiting');
            } else if (status.startsWith("снято с публикации")) {
                console.log(`Статус снято с публикации для объявления с ID: ${announcementId}`);
                copyButton.hide();
                takeoffButton.hide();
                statusIcon.removeClass('status-published status-awaiting').addClass('status-removed');
                $row.addClass('inactive-row');
            } else {
                $row.removeClass('inactive-row');
            }

            if (!status.startsWith("снято с публикации")) {
                console.log(`Статус не снято с публикации для объявления с ID: ${announcementId}`);
                $row.removeClass('table-secondary');
            }

            const publicationDate = formatDate(new Date(data.publication_date));
            if (["опубликовано", "ожидает публикации"].includes(status)) {
                console.log(`Добавление времени публикации к статусу для объявления с ID: ${announcementId}`);
                status += ` ${publicationDate}`;
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
