window.executeAjax = function (page) {
    console.log("Inside executeAjax function");

    var nameFilter = $("#nameFilter").val();
    var tagFilter = $("#tagFilter").val();
    var statusFilter = $("#statusFilter").val();
    console.log("Selected page:", page);
    console.log("Name filter:", nameFilter);
    console.log("Tag filter:", tagFilter);
    console.log("Status filter:", statusFilter);
    $.ajax({
        type: "GET",
        url: "/announcements/all",
        data: {
            page: page,
            nameFilter: nameFilter,
            tagFilter: tagFilter,
            statusFilter: statusFilter,
        },
        dataType: "html",
        success: function (data) {
            console.log("Ajax request successful");

            var new_page = $(data);
            console.log("New page content:", new_page);

            $("#announcementsTable").replaceWith(
                new_page.find("#announcementsTable")
            );
            console.log("Replaced announcements table");

            $("#pagination").replaceWith(new_page.find("#pagination"));
            console.log("Replaced pagination");

            updateStatuses();
            updateMediaMap();
        },
    });
}

function debounce(func, wait, immediate) {
    var timeout;
    return function () {
        var context = this, args = arguments;
        var later = function () {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
};

var executeAjaxDebounced = debounce(executeAjax, 250);


window.handlePaginationEvents = function () {
    console.log("Inside handlePaginationEvents function");

    $("#pagination").on("click", "a", function (e) {
        console.log("Pagination link clicked");
        e.preventDefault();
        var page = $(this).attr("href").split("page=")[1];
        executeAjax(page);
    });

    $("#nameFilter").on("input", function () {
        console.log("Name filter input detected");
        var page = $("#pagination .active").text();
        executeAjaxDebounced(page);
    });
    $("#tagFilter").on("input", function () {
        console.log("Tag filter input detected");
        var page = $("#pagination .active").text();
        executeAjaxDebounced(page);
    });
    $("#statusFilter").on("change", function () {
        console.log("Status filter input detected");
        var page = $("#pagination .active").text();
        executeAjaxDebounced(page);
    });
}
