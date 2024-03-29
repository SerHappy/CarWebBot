$(document).ready(function () {
    $(document).on('click', '#deleteModalButton', function () {
        $("#deleteModal").modal('show');
        let deleteUrl = $(this).data('delete-url');
        let redirectUrl = $(this).data('redirect-url');

        $("#deleteButton").click(function () {
            let cookie = document.cookie;
            let csrfToken = cookie.substring(cookie.indexOf('=') + 1);
            $.ajax({
                url: deleteUrl,
                type: 'DELETE',
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
