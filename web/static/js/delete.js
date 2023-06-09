$(document).ready(function () {
    $(document).on('click', '#deleteModalButton', function () {
        // Получить JSON объявления из data-атрибута
         let announcementId = $(this).data('announcement-id');
        console.log(announcementId);

        $("#deleteModal").modal('show');

        // Когда кнопка в модальном окне нажата...
        $("#deleteButton").click(function () {
            let cookie = document.cookie
            let csrfToken = cookie.substring(cookie.indexOf('=') + 1)
            $.ajax({
                url: '/announcements/delete/' + announcementId + '/',
                type: 'POST',
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                },
                success: function () {
                    window.location.href = "/";
                },
                error: function () {
                    alert('Произошла ошибка при удалении объявления');
                }
            });
        });
    });
});
