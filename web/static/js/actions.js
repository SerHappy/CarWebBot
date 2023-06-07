$(document).ready(function () {
  $(document).on('click', '.takeoff-button', function () {
    console.log("takeoffButton clicked!")
    let announcementId = $(this).closest('.announcement-row').data('announcement-id');
    console.log("announcementId: " + announcementId)
    let cookie = document.cookie
    let csrfToken = cookie.substring(cookie.indexOf('=') + 1)
    $.ajax({
      url: '/announcements/takeoff/' + announcementId,
      type: 'POST',
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-CSRFToken", csrfToken);
      },
      success: function () {
        alert('Объявление было успешно снято с публикации');
        updateStatuses();
      },
      error: function () {
        alert('Произошла ошибка при снятии объявления с публикации');
      }
    });
  });


  $(document).on('click', '.republish-button', function () {
    let announcementId = $(this).closest('.announcement-row').data('announcement-id');
    let cookie = document.cookie
    let csrfToken = cookie.substring(cookie.indexOf('=') + 1)
    // Показать модальное окно
    $("#republishModal").modal('show');

    // Когда кнопка в модальном окне нажата...
   $("#republishButton").off('click').click(function () {
      let republishDatetime = $("#new_publication_date").val();
      let timezone = $("#timezone").val();
      $.ajax({
        url: '/announcements/republish/' + announcementId + '/',
        type: 'POST',
        beforeSend: function (xhr) {
          // Добавить CSRF токен в заголовки запроса
          xhr.setRequestHeader("X-CSRFToken", csrfToken);
        },
        data: {
          datetime: republishDatetime,
          timezone: timezone
        },
        success: function () {
          alert('Объявление было успешно переопубликовано');
          updateStatuses();
        },
        error: function () {
          alert('Произошла ошибка при переопубликовании объявления');
        }
      });

      // Скрыть модальное окно
      $("#republishModal").modal('hide');
    });
  });
});
