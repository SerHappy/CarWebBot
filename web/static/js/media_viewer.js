var currentMediaIndex = -1;
var currentRowId = null;
var mediaMap = {};

function updateMediaMap() {
    mediaMap = {};
    $(".media-links").each(function () {
        var rowId = $(this).data("announcement-id");
        if (!(rowId in mediaMap)) {
            mediaMap[rowId] = [];
        }
        mediaMap[rowId].push($(this).data("src"));
    });
}


$("#previous").on("click", function () {
    if (currentMediaIndex > 0) {
        currentMediaIndex--;
        loadMedia(mediaMap[currentRowId][currentMediaIndex]);
    }
    checkButtonStatus();
});

$("#next").on("click", function () {
    if (currentMediaIndex < mediaMap[currentRowId].length - 1) {
        currentMediaIndex++;
        loadMedia(mediaMap[currentRowId][currentMediaIndex]);
    }
    checkButtonStatus();
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
    updateMediaCounter();
}

function updateMediaCounter() {
    $('#media-counter').text((currentMediaIndex + 1) + '/' + mediaMap[currentRowId].length);
}

function checkButtonStatus() {
    $('#previous').prop('disabled', currentMediaIndex === 0);
    $('#next').prop('disabled', currentMediaIndex === mediaMap[currentRowId].length - 1);
}

$("#mediaModal").on("show.bs.modal", function (event) {
    var button = $(event.relatedTarget);
    currentRowId = button.data("announcement-id");
    updateMediaMap();
    var src = button.data("src");
    currentMediaIndex = mediaMap[currentRowId].indexOf(src);
    loadMedia(src);
    checkButtonStatus();
});
$(document).keydown(function (e) {
    switch (e.which) {
        case 37:
            $("#previous").trigger('click');
            break;
        case 39:
            $("#next").trigger('click');
            break;
        default: return;
    }
    e.preventDefault();
});
