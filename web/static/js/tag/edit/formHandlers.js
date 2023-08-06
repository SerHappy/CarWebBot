$(document).ready(function () {
  $('button[type="reset"]').click(function () {
    setTimeout(function () { $('#tagName').trigger('change'); }, 10);
  });
  $('#tagName').on('change', function () {
    var tagName = $(this).val().trim();
    var tagId = $(this).data('tag-id');
    var defaultTagName = $(this).data('default-tag-name');
    var checkURL = $(this).data('check-url');

    if (tagName.trim() == '') {
      $('#tagName').removeClass('is-valid').addClass('is-invalid');
      $('#tagHelp').text("Пожалуйста, введите имя тега.").addClass('text-danger');
    } else {
      $.ajax({
        url: checkURL,
        data: {
          'tag_name': tagName,
          'tag_id': tagId,
        },
        dataType: 'json',
        success: function (data) {
          if (data.is_taken) {
            $('#tagName').removeClass('is-valid').addClass('is-invalid');
            $('#tagHelp').text("Тег с таким именем уже существует.").addClass('text-danger');
          } else {
            if (tagName == defaultTagName) {
              $('#tagName').removeClass('is-invalid').removeClass('is-valid');
              $('#tagHelp').text("Имя тега не изменилось.").removeClass('text-danger').removeClass('text-success');
            } else {
              $('#tagName').removeClass('is-invalid').addClass('is-valid');
              $('#tagHelp').text("Тег с таким именем доступен.").removeClass('text-danger').addClass('text-success');
            }
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
