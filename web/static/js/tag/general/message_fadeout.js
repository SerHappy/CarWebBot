$(document).ready(function () {
    window.setTimeout(function () {
        $(".alert-success, .alert-danger").fadeTo(300, 0).slideUp(300, function () {
            $(this).remove();
        });
    }, 1500);
});
