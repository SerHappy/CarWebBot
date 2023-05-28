
$(document).ready(function () {
    var currentMediaIndex = -1;
    var currentRowId = null;
    var mediaMap = {};

    window.updateMediaMap = function () {
        mediaMap = {};
        $(".media-links").each(function () {
            var rowId = $(this).data("announcement-id");
            if (!(rowId in mediaMap)) {
                mediaMap[rowId] = [];
            }
            mediaMap[rowId].push($(this).data("src"));
        });
    }

    $(".media-links").each(function () {
        var rowId = $(this).data("announcement-id");
        if (!(rowId in mediaMap)) {
            mediaMap[rowId] = [];
        }
        mediaMap[rowId].push($(this).data("src"));
    });

    $("#mediaModal").on("show.bs.modal", function (event) {
        var button = $(event.relatedTarget);
        currentRowId = button.data("announcement-id");
        currentMediaIndex = button.data("media-index");
        var src = button.data("src");
        loadMedia(src);
    });

    $("#previous").on("click", function () {
        if (currentMediaIndex > 0) {
            currentMediaIndex--;
            loadMedia(mediaMap[currentRowId][currentMediaIndex]);
        }
    });

    $("#next").on("click", function () {
        console.log(currentMediaIndex);
        console.log(mediaMap);
        if (currentMediaIndex < mediaMap[currentRowId].length - 1) {
            currentMediaIndex++;
            loadMedia(mediaMap[currentRowId][currentMediaIndex]);
        }
    });

    function loadMedia(src) {
        var mediaHtml;
        if (src.endsWith(".mp4") || src.endsWith(".mov")) {
            mediaHtml =
                '<video controls><source src="' +
                src +
                '" type="video/mp4">Your browser does not support the video tag.</video>';
        } else {
            mediaHtml = '<img src="' + src + '" class="img-fluid">';
        }
        $("#mediaModal").find(".modal-body").html(mediaHtml);
    }
});
