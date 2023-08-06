$(document).ready(function () {
  $('#tagName').on('change', function () {
    var tagName = $(this).val().trim();
    var checkURL = $(this).data('check-url');
    if (tagName.trim() == '') {
      $('#tagName').removeClass('is-valid').addClass('is-invalid');
      $('#tagHelp').text("Пожалуйста, введите имя тега.").addClass('text-danger');
    } else {
      $.ajax({
        url: checkURL,
        data: {
          'tag_name': tagName
        },
        dataType: 'json',
        success: function (data) {
          if (data.is_taken) {
            $('#tagName').removeClass('is-valid').addClass('is-invalid');
            $('#tagHelp').text("Тег с таким именем уже существует.").addClass('text-danger');
          } else {
            $('#tagName').removeClass('is-invalid').addClass('is-valid');
            $('#tagHelp').text("Тег с таким именем доступен.").removeClass('text-danger').addClass('text-success');
          }
        }
      });
    }
  });

  $('#tag-form').on('submit', function (event) {
    if ($('#tagName').hasClass('is-invalid')) {
      event.preventDefault();
      alert('Пожалуйста, исправьте ошибки перед отправкой формы.');
    }
  });
});
