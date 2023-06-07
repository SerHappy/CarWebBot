window.updateStatuses = function() {
    console.log("Updating statuses");

    // Запросить статус для каждого объявления
    $("#announcementsTable .announcement-row").each(function() {
      var row = $(this);
      var announcementId = row.data("announcement-id");
      console.log("Requesting status for announcement:", announcementId);
        $.ajax({
    type: "GET",
    url: "/announcements/status/" + announcementId + "/",
    dataType: "json",
    success: function (data) {
        console.log(data);
        console.log("Received status for announcement:", announcementId);
        console.log("Status:", data.status);

        var copyButton = row.find(".copy-button");
        console.log("Copy button:", copyButton);
        if (data.status.toLowerCase().startsWith("опубликовано")) {
                console.log("Show copy button");
                 copyButton.show();
        } else {
                console.log("Hide copy button");
                copyButton.hide();
            }

        // Переводим дату в нужный формат
        let date = new Date(data.publication_date);
        let hours = date.getHours();
        let minutes = date.getMinutes();
        let timeString = hours + ":" + (minutes < 10 ? '0' : '') + minutes;
        console.log("Time string:", timeString);

        // Если статус равен "Опубликовано" или "Ожидает публикации", добавляем время публикации
        if (["опубликовано", "ожидает публикации"].includes(data.status.toLowerCase())) {
            console.log("Add publication time");
            data.status += " в " + timeString;
        }

        // Обновить статус в таблице
        row.find("#status_text_" + announcementId).text(data.status);

        // Если статус равен "снято с публикации", красить строку серым
        if (data.status.toLowerCase().startsWith("снято с публикации")) {
            row.addClass('inactive-row');
        } else {
            row.removeClass('inactive-row');
        }
    },
});
    });
}
