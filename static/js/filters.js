console.log("ready");
$(document).ready(function () {
  console.log("ready");
  function filterTable() {
    const nameFilter = $("#nameFilter").val().toLowerCase();
    const tagFilter = $("#tagFilter").val().toLowerCase();

    // Отправьте запрос на сервер с параметрами фильтрации
    $.ajax({
      url: "/",
      type: "GET",
      data: {
        name_filter: nameFilter,
        tag_filter: tagFilter,
      },
      success: function (response) {
        // Замените содержимое таблицы и пагинации новыми данными
        const newTable = $(response).find("#announcementsTable");
        const newPagination = $(response).find(".card-footer");
        $("#announcementsTable").replaceWith(newTable);
        $(".card-footer").replaceWith(newPagination);
      },
    });
  }

  $("#nameFilter").on("input", filterTable);
  $("#tagFilter").on("input", filterTable);
});
