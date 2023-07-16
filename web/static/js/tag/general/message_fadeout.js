$(document).ready(function () {
window.setTimeout(function() {
        $(".alert").fadeTo(350, 0).slideUp(350, function() {
            $(this).remove();
        });
    }, 350);
});
