var mockFileCount = 0;
console.log("Initializing Dropzone");
Dropzone.autoDiscover = false;
var myDropzone = new Dropzone("#dropzoneForm", {
  url: "{{ action }}",
  autoProcessQueue: false,
  uploadMultiple: true,
  parallelUploads: 100,
  maxFilesize: 50, // 50 MB
  addRemoveLinks: true,
  filesizeBase: 1024,
  resizeQuality: 2,
  previewTemplate: `
    <div class="dz-preview dz-file-preview">
      <div class="dz-image"><img data-dz-thumbnail /></div>
    </div>`,
  previewsContainer: "#dropzoneForm",
  acceptedFiles: "image/jpeg,video/mp4",
  paramName: "media",
});
console.log("Adding event listener for form submit");
document
  .querySelector("#announcement-form")
  .addEventListener("submit", function (e) {
    console.log("Form submit triggered");
    e.preventDefault();
    e.stopPropagation();
    shouldSubmitForm = true;
    var dataTransfer = new DataTransfer();
    console.log("Processing accepted files");
    myDropzone.getAcceptedFiles().forEach(function (file) {
      console.log("Adding accepted file to dataTransfer:");
      console.log(file);
      dataTransfer.items.add(file);
    });

    var existingFilesValue = document.querySelector("#existing-files").value;
    console.log("Existing files value: " + existingFilesValue);
    console.log(dataTransfer.items.length);
    console.log(existingFilesValue.trim());
    if (dataTransfer.items.length == 0 && existingFilesValue.trim() == "") {
      console.log("No files for upload, displaying error");
      alert("Загрузка файла обязательна!");
      return;
    }

    console.log("Setting files to #file-upload");
    document.querySelector("#file-upload").files = dataTransfer.files;

    console.log("Submitting form");
    e.currentTarget.submit();
  });

myDropzone.on("queuecomplete", function () {
  console.log("Queue complete triggered");
  if (shouldSubmitForm) {
    console.log("Submitting form");
    document.querySelector("#announcement-form").submit();
  }
});

myDropzone.on("addedfile", function (file) {
  console.log("Addedfile event triggered for file: " + file.name);

  if (!isExistingFileBeingAdded) {
    if (
      !existingFiles.find((existingFile) => existingFile.name === file.name)
    ) {
      console.log("Adding file to existingFiles array");
      existingFiles.push(file);
      console.log("Current existingFiles array:");
      console.log(existingFiles);
    }
  }
  else {
    mockFileCount += 1;
  }

  if (myDropzone.files.length > 0 || mockFileCount > 0) {
    console.log("Files exist, hiding dz-message");
    document.querySelector(".dz-message").style.display = "none";
  }
  checkFileCountAndUpdateButton();
});

console.log("Initial files in myDropzone.files:");
console.log(myDropzone.files);

myDropzone.on("removedfile", function (file) {
    var fileToRemove = file.name.substr(7);
    console.log("Removedfile event triggered for file: " + fileToRemove);
    console.log("Current existingFiles array:");
    console.log(existingFiles);

    let index = existingFiles.findIndex(
        (existingFile) => existingFile.name === file.name
    );
    if (index != -1) {
        console.log("Removing file from existingFiles array");
        existingFiles.splice(index, 1); // Удаляем файл из existingFiles
        console.log("Updated existingFiles array:");
        console.log(existingFiles);
        // Уменьшаем mockFileCount только если удаленный файл является мок-файлом
        if (file.isMock) {
            mockFileCount -= 1;
        }
    }

    let existingFilesInput = document.querySelector("#existing-files");
    let existingFilesArray = existingFilesInput.value.split(",");
    console.log("Current existingFilesArray:");
    console.log(existingFilesArray);
    let fileIndex = existingFilesArray.indexOf(fileToRemove);
    if (fileIndex >= 0) {
        console.log("Removing file name from #existing-files input value");
        existingFilesArray.splice(fileIndex, 1);
        existingFilesInput.value = existingFilesArray.join(",");
    }

    if (myDropzone.files.length > 0 || mockFileCount > 0) {
        console.log("Files exist, hiding dz-message");
        document.querySelector(".dz-message").style.display = "none";
    } else {
        console.log("No files exist, displaying dz-message");
        document.querySelector(".dz-message").style.display = "block";
    }
    checkFileCountAndUpdateButton();
});

myDropzone.on("error", function(file, message) {
  if (message.indexOf("File is too big") !== -1) {
    alert("Файл слишком большой. Максимальный размер файла - 50 МБ.");
  } else if (message === "You can't upload files of this type.") {
    alert("Неподдерживаемый формат файла. Пожалуйста, загрузите файлы формата .jpg или .mp4.");
  }
  this.removeFile(file);
});


function checkFileCountAndUpdateButton() {
  let editButton = document.getElementById('editButton'); // Получаем кнопку "Редактировать"
  console.log("Current editButton:");
  console.log(editButton);
  // Если кнопка "Редактировать" существует
  if (editButton) {
  console.log("Checking file count");
  let currentFileCount = myDropzone.files.length + mockFileCount; // Считаем текущее количество файлов
  console.log("Current file count: " + currentFileCount);
  console.log("myDropzone files: ");
  console.log(myDropzone.files);
  console.log("mockFileCount: " + mockFileCount);
    // Если текущее количество файлов отличается от изначального, делаем кнопку неактивной
    if (currentFileCount != initialFileCount) {
      console.log("File count differs from initial, disabling editButton");
      editButton.setAttribute('disabled', 'disabled');
      if (currentFileCount > initialFileCount) {
        editButton.setAttribute('title', 'Количество файлов увеличилось, редактирование невозможно. Было: ' + initialFileCount + ', стало ' + currentFileCount + '');
      } else {
        editButton.setAttribute('title', 'Количество файлов уменьшилось, редактирование невозможно. Было ' + initialFileCount + ', стало ' + currentFileCount + '');
      }
    } else {
      // Иначе делаем кнопку активной
      console.log("File count is the same as initial, enabling editButton");
      editButton.removeAttribute('disabled');
      editButton.setAttribute('title', '');
    }
  }
}

$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})
