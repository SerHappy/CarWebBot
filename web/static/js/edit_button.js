function checkFileCountAndUpdateButton() {
  let currentFileCount = myDropzone.files.length + mockFileCount; // Считаем текущее количество файлов
  let editButton = document.getElementById('editButton'); // Получаем кнопку "Редактировать"

  // Если текущее количество файлов отличается от изначального, делаем кнопку неактивной
  if (currentFileCount !== initialFileCount) {
    editButton.setAttribute('disabled', 'disabled');
  } else {
    // Иначе делаем кнопку активной
    editButton.removeAttribute('disabled');
  }
}
