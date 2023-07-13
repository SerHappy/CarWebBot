$(document).ready(function () {
    $(document).on('click', '#deleteModalButton', function () {
        $("#deleteModal").modal('show');

        $("#deleteButton").click(function () {
            let deleteUrl = $(this).data('delete-url');
            let redirectUrl = $(this).data('redirect-url');
            let cookie = document.cookie;
            let csrfToken = cookie.substring(cookie.indexOf('=') + 1);
            $.ajax({
                url: deleteUrl,
                type: 'POST',
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                },
                success: function () {
                    window.location.href = redirectUrl;
                },
                error: function () {
                    alert('Произошла ошибка при удалении тега');
                }
            });
        });
    });
});
