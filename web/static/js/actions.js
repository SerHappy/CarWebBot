$(".btn-warning").click(function() {
  let announcementId = $(this).closest('.announcement-row').data('announcement-id');
    let cookie = document.cookie
    let csrfToken = cookie.substring(cookie.indexOf('=') + 1)
  $.ajax({
    url: '/announcements/disable/' + announcementId + '/',
      type: 'POST',
    beforeSend: function(xhr) {
      // Добавить CSRF токен в заголовки запроса
      xhr.setRequestHeader("X-CSRFToken", csrfToken);
    },
    success: function() {
      alert('Объявление было успешно снято с публикации');
        updateStatuses();
    },
    error: function() {
      alert('Произошла ошибка при снятии объявления с публикации');
    }
  });
});


$("#republishModalButton").click(function () {
  let announcementId = $(this).closest('.announcement-row').data('announcement-id');
    let cookie = document.cookie
    let csrfToken = cookie.substring(cookie.indexOf('=') + 1)
  // Показать модальное окно
  $("#republishModal").modal('show');

  // Когда кнопка в модальном окне нажата...
  $("#republishButton").click(function() {
    let republishDatetime = $("#new_publication_date").val();
    let timezone = $("#timezone").val();
    $.ajax({
      url: '/announcements/republish/' + announcementId + '/',
        type: 'POST',
       beforeSend: function(xhr) {
      // Добавить CSRF токен в заголовки запроса
      xhr.setRequestHeader("X-CSRFToken", csrfToken);
    },
      data: {
          datetime: republishDatetime,
            timezone: timezone
      },
      success: function() {
          alert('Объявление было успешно переопубликовано');
          updateStatuses();
      },
      error: function() {
        alert('Произошла ошибка при переопубликовании объявления');
      }
    });

    // Скрыть модальное окно
    $("#republishModal").modal('hide');
  });
});
