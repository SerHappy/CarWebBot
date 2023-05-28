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
                // Обновить статус в таблице
            row.find("#status_" + announcementId).text(data.status);

            console.log("Status:", data.status);
            // Если статус равен "снято с публикации", красить строку серым
            if (data.status.toLowerCase() === "снято с публикации") {
                row.addClass('inactive-row');
            } else {
                row.removeClass('inactive-row');
            }
            },
        });
    });
}
