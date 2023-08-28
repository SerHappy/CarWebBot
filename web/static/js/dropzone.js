Dropzone.autoDiscover = false;
class MyDropzone {
  constructor() {
    this.myDropzone = null;
    this.shouldSubmitForm = false;
    this.uploadIds = [];
  }

  get dropzoneOptions() {
    let cookie = document.cookie
    let csrfToken = cookie.substring(cookie.indexOf('=') + 1)
    return {
      url: '/announcements/media/add/',
      autoProcessQueue: true,
      uploadMultiple: false,
      parallelUploads: 3,
      maxFilesize: 50,
      addRemoveLinks: true,
      filesizeBase: 1000,
      resizeQuality: 2,
      acceptedFiles: "image/jpeg,video/mp4",
      paramName: "media",
      previewsContainer: "#dropzoneForm",
      init: () => this.initDropzone(),
      previewTemplate: `
      <div class="dz-preview dz-file-preview">
        <div class="dz-image">
          <img data-dz-thumbnail />
        </div>
        <div class="dz-details">
          <div class="dz-size"><span data-dz-size></span></div>
        </div>
        <div class="dz-progress"><span class="dz-upload" data-dz-uploadprogress></span></div>
        <div class="dz-success-mark"><span></span></div>
      <div class="dz-error-mark"><span></span></div>
      <div class="dz-error-message"><span data-dz-errormessage></span></div>
      </div>`,
      headers: {
        'X-CSRFToken': csrfToken,
      },
      accept: function (file, done) {
        if (file.type.startsWith('image/')) {
          if (file.size > 10 * 1024 * 1024) {
            console.log("File type: " + file.type);
            console.log("Media file size: " + file.size);
            done("Файл изображения слишком большой. Максимальный размер файла изображения - 10 МБ.");
          } else {
            let img = new Image();
            img.onload = function () {
              console.log("Image onload triggered");
              let width = this.width;
              console.log("Image width: " + width);
              let height = this.height;
              console.log("Image height: " + height);
              if ((width + height) > 10000 || (width / height > 20) || (height / width > 20)) {
                console.log("Image size is too big");
                done("Размеры изображения слишком большие. Сумма ширины и высоты не должна превышать 10000, а соотношение сторон должно быть не более 20.");
              } else {
                done();
              }
            };
            img.src = URL.createObjectURL(file);
          }
        } else if (file.type.startsWith('video/')) {
          file.previewElement.classList.add('dz-video-preview');
          let videoIcon = document.createElement('i');
          videoIcon.classList.add('fas', 'fa-video', 'video-icon');
          file.previewElement.appendChild(videoIcon);
          if (file.size > 50 * 1024 * 1024) {
            console.log("File type: " + file.type);
            console.log("Media file size: " + file.size);
            done("Файл видео слишком большой. Максимальный размер файла видео - 50 МБ.");
          } else {
            let video = document.createElement('video');
            console.log("Video created");
            video.preload = 'metadata';
            video.onloadedmetadata = function () {
              window.URL.revokeObjectURL(video.src);
              let width = video.videoWidth;
              console.log("Video width: " + width);
              let height = video.videoHeight;
              console.log("Video height: " + height);
              if ((width + height) > 10000 || (width / height > 20) || (height / width > 20)) {
                console.log("Video size is too big");
                done("Размеры видео слишком большие. Сумма ширины и высоты не должна превышать 10000, а соотношение сторон должно быть не более 20.");
              } else {
                done();
              }
            };
            video.src = URL.createObjectURL(file);
          }
        } else {
          done();
        }
      },
      success: (file, response) => {
        console.log('File:', file);
        console.log('Response:', response);
        file.uploadId = response.uploadId;
        console.log("File uploadId: " + file.uploadId);
      },
    };
  }

  initDropzone() {
    console.log("Dropzone init triggered");
    $("#dropzoneForm").sortable({
      items: '.dz-preview',
      cursor: 'move',
      opacity: 0.3,
      containment: "#dropzoneForm",
      distance: 20,
      tolerance: 'pointer',
      forcePlaceholderSize: true,
      update: (e, ui) => {
        console.log("Sortable update triggered");
        this.updateFileOrderInDropzone(this.myDropzone);
      }
    });
  }

  displayExistingFile(file, url) {
    console.log("Display existing file triggered");
    console.log("File: ");
    console.log(file);
    console.log("Url: ");
    console.log(url);
    this.myDropzone.displayExistingFile(file, url);
  }

  processAcceptedFiles(formData) {
    this.myDropzone.getAcceptedFiles().forEach(function (file) {
      console.log("Accepted file: " + file.name);
      formData.append('uploadIds', file);
    });
  }

  addEventListener() {
    document
      .querySelector("#announcement-form")
      .addEventListener("submit", (e) => this.submitForm(e));
  }

  submitForm(e) {
    console.log("Submit form triggered");
    if (this.myDropzone.files.length == 0) {
      e.preventDefault();
      alert("Пожалуйста, загрузите хотя бы один файл");
    }
    else {
      console.log("Submit form triggered");
      const form = document.getElementById('announcement-form');
      const input = document.createElement('input');
      this.uploadIds = this.getOrderedUploadIds();
      input.type = 'hidden';
      input.name = 'uploadIds';
      input.value = this.uploadIds;
      console.log("input.value");
      console.log(input.value);

      form.appendChild(input);

      // Submit the form
      form.submit();
    }

  }

  queueComplete() {
    console.log("Queue complete triggered");
    if (this.shouldSubmitForm) {
      console.log("Submitting form");
      document.querySelector("#announcement-form").submit();
    }
  }

  addedFile(file) {
    console.log("Addedfile event triggered for file: " + file.name);
    file.index = this.myDropzone.files.indexOf(file);
    file.order = this.myDropzone.files.length - 1;
    console.log("File " + file.name + " index: " + file.index + " order: " + file.order);
    console.log("Current uploadIds array:");
    console.log(this.uploadIds);
    console.log("Current file.type: " + file.type);

    if (file.type.startsWith("video") || file.type.startsWith("VIDEO")) {
      file.previewElement.classList.add('dz-video-preview');
      let videoIcon = document.createElement('i');
      videoIcon.classList.add('fas', 'fa-video', 'video-icon');
      file.previewElement.appendChild(videoIcon);
    }

    if (file.type.startsWith("video")) {
      console.log("Это видео");

      // Создаем Blob и временный URL для видео
      const blob = new Blob([file], { type: 'video/mp4' });
      const url = URL.createObjectURL(blob);
      console.log(`Создан временный URL для видео: ${url}`);

      // Создаем элементы video и canvas
      const video = document.createElement('video');
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      // Задаем исходный URL для video
      video.src = url;

      // Когда метаданные видео загружены
      video.addEventListener('loadedmetadata', function () {
        console.log(`Метаданные загружены`);

        // Получаем размеры элемента превью
        const previewWidth = file.previewElement.querySelector(".dz-image").offsetWidth;
        const previewHeight = file.previewElement.querySelector(".dz-image").offsetHeight;

        // Устанавливаем размеры холста согласно размерам превью
        canvas.width = previewWidth;
        canvas.height = previewHeight;

        video.currentTime = 1; // Переход к 1-й секунде
      });

      // Когда видео готово к отрисовке на холсте
      video.addEventListener('seeked', function () {
        // Рисуем изображение на холсте с учетом размеров превью
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imgDataUrl = canvas.toDataURL();

        // Заменяем превью видео изображением
        file.previewElement.querySelector(".dz-image").innerHTML = `<img src="${imgDataUrl}" />`;
        console.log(`Превью создано`);
      });

      // Обработка ошибок
      video.addEventListener('error', function (e) {
        console.log(`Ошибка при обработке видео: ${file.name}`);
        console.log('Детали ошибки:', e);
      });
      file.previewElement.classList.remove("dz-file-preview");
    }


    if (this.myDropzone.files.length > 0) {
      console.log("Files exist, hiding dz-message");
      document.querySelector(".dz-message").style.display = "none";
    }
    this.checkFileCountAndUpdateButton();
  }

  removedFile(file) {
    console.log("UploadIds before removal:");
    console.log(this.uploadIds);
    console.log("Removedfile event triggered for file: " + file.name);
    console.log("this.myDropzone.files");
    for (var i = 0; i < this.myDropzone.files.length; i++) {
      console.log(this.myDropzone.files[i].name);
    }
    if (file.status !== 'error') {
      console.log("Removed file event triggered for file: ", file.uploadId);

      let csrfToken = document.cookie.substring(document.cookie.indexOf('=') + 1);
      console.log("CSRF token extracted from cookie: ", csrfToken);

      // Удаление файла с сервера
      let xhr = new XMLHttpRequest();
      xhr.open('DELETE', '/announcements/media/delete/' + encodeURIComponent(file.uploadId) + "/");
      xhr.setRequestHeader('X-CSRFToken', csrfToken);
      xhr.send();
      console.log("File removal request sent to server for file: ", file.uploadId);

      // Обработка ответа сервера
      xhr.onload = function () {
        if (xhr.status != 200) {
          console.log(`Server responded with error ${xhr.status}: ${xhr.statusText}`);
        } else {
          let responseJson = JSON.parse(xhr.response);
          console.log(`Done, server responded with: `, responseJson);
        }
      };

      xhr.onerror = function () {
        console.log('Request to server failed');
      };
    }
    if (file.uploadId !== undefined) {
      let fileIndexInDropzone = this.myDropzone.files.findIndex((dropzoneFile) => dropzoneFile.uploadId === file.uploadId);
      console.log("File index in Dropzone files array: ", fileIndexInDropzone);
      if (fileIndexInDropzone != -1) {
        this.myDropzone.files.splice(fileIndexInDropzone, 1);
        console.log("File removed from Dropzone files array");
      }

      // Update uploadIds
      this.uploadIds = this.myDropzone.files.map(file => file.uploadId);
    }

    console.log("Updated Dropzone files array: ", this.myDropzone.files);
    console.log("Updated UploadIds: ", this.uploadIds);
    console.log("Updating Dropzone files array: ", this.myDropzone.files);
    for (let i = 0; i < this.myDropzone.files.length; i++) {
      this.myDropzone.files[i].order = i;
      this.myDropzone.files[i].index = i;
    }
    console.log("Updated Dropzone files array: ", this.myDropzone.files);
    console.log("UploadIds");
    console.log(this.uploadIds);
    // Обновление интерфейса
    if (this.myDropzone.files.length > 0) {
      document.querySelector(".dz-message").style.display = "none";
      console.log("Files exist, hiding dz-message");
    } else {
      document.querySelector(".dz-message").style.display = "block";
      console.log("No files exist, displaying dz-message");
    }

    this.checkFileCountAndUpdateButton();
  }

  handleError(file, message) {
    if (message.startsWith("Файл изображения слишком большой")) {
      alert("Файл изображения слишком большой. Максимальный размер файла изображения - 10 МБ.");
    } else if (message.startsWith("Файл видео слишком большой")) {
      alert("Файл видео слишком большой. Максимальный размер файла видео - 50 МБ.");
    } else if (message === "You can't upload files of this type.") {
      alert("Неподдерживаемый формат файла. Пожалуйста, загрузите файлы формата .jpg или .mp4.");
    } else if (message.startsWith("Размеры изображения слишком большие.")) {
      alert("Размеры изображения слишком большие. Сумма ширины и высоты не должна превышать 10000, а соотношение сторон должно быть не более 20.");
    } else if (message.startsWith("Размеры видео слишком большие.")) {
      alert("Размеры видео слишком большие. Сумма ширины и высоты не должна превышать 10000, а соотношение сторон должно быть не более 20.");
    }
    file.status = "error";
    this.myDropzone.removeFile(file);
  }


  checkFileCountAndUpdateButton() {
    let editButton = document.getElementById('editButton'); // Получаем кнопку "Редактировать"
    console.log("Current editButton:");
    console.log(editButton);
    // Если кнопка "Редактировать" существует
    if (editButton) {
      console.log("Checking file count");
      let currentFileCount = this.myDropzone.files.length; // Считаем текущее количество файлов
      console.log("Current file count: " + currentFileCount);
      console.log("myDropzone files: ");
      console.log(this.myDropzone.files);
      // Если текущее количество файлов отличается от изначального, делаем кнопку неактивной
      console.log("Initial file count: " + initialFileCount);
      let announcementData = editButton.getAttribute('data-announcement');
      let announcement = JSON.parse(announcementData);
      console.log("announcement: ", announcement);
      console.log(announcement[0].fields.processing_status);
      if (currentFileCount > initialFileCount) {
        console.log("File count more than initialFileCount, disabling editButton");
        editButton.setAttribute('disabled', 'disabled');
        editButton.setAttribute('title', 'Количество файлов увеличилось, редактирование невозможно. Было: ' + initialFileCount + ', стало ' + currentFileCount + '');
      }
      else {
        if (announcement[0].fields.processing_status != "PUBLISHED") {
          console.log("Announcement is not published, disabling editButton");
          editButton.setAttribute('disabled', 'disabled');
          editButton.setAttribute('title', 'Объявление не опубликовано, редактирование невозможно');
        } else {
          console.log("File count is the same as initial, enabling editButton");
          editButton.removeAttribute('disabled');
          editButton.setAttribute('title', 'Редактирование разрешено');
        }
      }
    }
  }

  updateFileOrderInDropzone() {
    console.log("Updating file order in dropzone");

    // Define a new array to hold the updated upload ids
    let updatedUploadIds = new Array(this.myDropzone.files.length);

    this.uploadIds = this.getOrderedUploadIds();
    console.log(this.uploadIds);

    // Use an arrow function to preserve `this`
    this.myDropzone.files.forEach((file) => {
      file.order = $(file.previewElement).index() - 1;
      console.log("File " + file.name + " index: " + this.myDropzone.files.indexOf(file) + " order: " + file.order);

      // Update the uploadIds array according to the new order
      updatedUploadIds[file.order] = this.uploadIds[this.myDropzone.files.indexOf(file)];
      console.log("Updated uploadIds array:");
      console.log(updatedUploadIds);
    });

    // Replace the old uploadIds array with the updated one
    this.uploadIds = updatedUploadIds;
    console.log("Updated uploadIds array:");
    console.log(this.uploadIds);
    console.log("Updated files in myDropzone.files:");
    console.log(this.getOrderedUploadIds());
  }

  getOrderedUploadIds() {
    return this.myDropzone.files.sort((a, b) => a.order - b.order).map(file => file.uploadId);
  }

  removeAllFiles() {
    let files = [...this.myDropzone.files];
    for (let file of files) {
      this.myDropzone.removeFile(file);
    }
    document.getElementById("removeAllFiles").blur();
  }



  initialize() {
    console.log("Initializing Dropzone");
    Dropzone.autoDiscover = false;
    this.myDropzone = new Dropzone("#dropzoneForm", this.dropzoneOptions);

    this.myDropzone.on("queuecomplete", () => this.queueComplete());
    this.myDropzone.on("addedfile", (file) => this.addedFile(file));
    this.myDropzone.on("removedfile", (file) => this.removedFile(file));
    this.myDropzone.on("error", (file, message) => this.handleError(file, message));
    this.myDropzone.on("sending", function (file, xhr, formData) {
      let fileOrder = file.order;
      console.log("Sending file order: " + fileOrder);
      formData.append("order", fileOrder);
    });

    document.getElementById("removeAllFiles").addEventListener("click", () => this.removeAllFiles());

    this.addEventListener();
    console.log("Initial files in myDropzone.files:");
    console.log(this.myDropzone.files);
    console.log("Initializing tooltips");
    $('[data-toggle="tooltip"]').tooltip();
  }

}
