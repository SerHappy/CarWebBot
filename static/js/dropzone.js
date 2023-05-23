Dropzone.autoDiscover = false;
var myDropzone = new Dropzone("#dropzoneForm", {
  url: "/announcement/add/",
  autoProcessQueue: false,
  uploadMultiple: true,
  parallelUploads: 100,
  addRemoveLinks: true,
  resizeQuality: 1,
  previewTemplate: `
    <div class="dz-preview dz-file-preview">
      <div class="dz-image"><img data-dz-thumbnail /></div>
    </div>`,
  previewsContainer: "#dropzoneForm",
  acceptedFiles: "image/*,video/*",
  paramName: "media",
});

document
  .querySelector("#announcement-form")
  .addEventListener("submit", function (e) {
    e.preventDefault();
    e.stopPropagation();

    if (myDropzone.getAcceptedFiles().length == 0) {
      // Отображаем сообщение об ошибке
      alert("Загрузка файла обязательна!");
      return;
    }

    var dataTransfer = new DataTransfer();
    myDropzone.getAcceptedFiles().forEach(function (file) {
      dataTransfer.items.add(file);
    });

    document.querySelector("#file-upload").files = dataTransfer.files;

    e.currentTarget.submit();
  });

myDropzone.on("queuecomplete", function () {
  document.querySelector("#total-progress").style.opacity = "0";
  document.querySelector("#dropzoneForm").submit();
});

myDropzone.on("addedfile", function (file) {
  $(file.previewElement).find(".dz-progress").hide();
});
