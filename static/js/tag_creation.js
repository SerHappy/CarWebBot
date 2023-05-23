function createTag() {
  var formData = $("#createTagForm").serialize();
  $.ajax({
    type: "POST",
    url: "/tag/add/",
    data: formData,
    success: function (response) {
      // Обновить список тегов
      if (response.status == "error") {
        alert(response.message);
        return;
      }
      $("#tags").append(
        "<option value='" + response.id + "'>" + response.name + "</option>"
      );
      // Закрыть модальное окно
      $("#createTagModal").modal("hide");
    },
    error: function (xhr, status, error) {
      console.log(xhr.responseText);
    },
  });
}

// Обработчик события submit для формы
$("#createTagForm").submit(function (event) {
  event.preventDefault();
  createTag();
});

// Обработчик клика кнопки "Создать"
$("#createTagButton").click(createTag);
