$(document).ready(function () {
  let cookie = document.cookie;
  let csrfToken = cookie.substring(cookie.indexOf('=') + 1);

  $(document).on('click', '.takeoff-button', async function () {
    console.log("Нажата кнопка takeoffButton");
    let announcementRow = $(this).closest('.announcement-row');
    let announcementId = announcementRow.data('announcement-id');
    console.log(`ID объявления: ${announcementId}`);

    console.log(`Начало процедуры снятия объявления с ID: ${announcementId} с публикации`);
    try {
      await $.ajax({
        url: `/announcements/takeoff/${announcementId}`,
        type: 'POST',
        beforeSend: function (xhr) {
          xhr.setRequestHeader("X-CSRFToken", csrfToken);
        },
      });

      console.log(`Объявление с ID: ${announcementId} успешно снято с публикации`);
      announcementRow.addClass('table-secondary');
      announcementRow.find(".takeoff-button").hide();
      updateStatuses();
    } catch (error) {
      console.error(`Ошибка при снятии объявления с ID: ${announcementId} с публикации:`, error);
      alert('Произошла ошибка при снятии объявления с публикации');
    }
  });

  $(document).on('click', '.republish-button', function () {
    console.log("Нажата кнопка republishButton");
    let announcementRow = $(this).closest('.announcement-row');
    let announcementId = announcementRow.data('announcement-id');
    console.log(`ID объявления: ${announcementId}`);

    // Показать модальное окно
    $("#republishModal").modal('show');

    // Когда кнопка в модальном окне нажата...
    $("#republishButton").off('click').click(async function () {
      console.log(`Начало процедуры переопубликования объявления с ID: ${announcementId}`);
      let republishDatetime = $("#new_publication_date").val();
      let timezone = $("#timezone").val();

      try {
        await $.ajax({
          url: `/announcements/republish/${announcementId}/`,
          type: 'POST',
          beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", csrfToken);
          },
          data: {
            datetime: republishDatetime,
            timezone: timezone
          },
        });

        console.log(`Объявление с ID: ${announcementId} успешно переопубликовано`);
        updateStatuses();
      } catch (error) {
        console.error(`Ошибка при переопубликовании объявления с ID: ${announcementId}:`, error);
        alert('Произошла ошибка при переопубликовании объявления');
      }

      // Скрыть модальное окно
      $("#republishModal").modal('hide');
    });
  });
});
