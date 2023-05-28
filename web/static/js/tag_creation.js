function createTag() {
  var formData = $("#createTagForm").serialize();
  console.log("Form Data:", formData);

  $.ajax({
    type: "POST",
    url: "/announcements/tags/add/",
    data: formData,
    success: function (response) {
      console.log("Success response:", response);

      // Update the list of tags
      if (response.status == "error") {
        alert(response.message);
        return;
      }

      console.log("Tag ID:", response.id);
      console.log("Tag Name:", response.name);

      $("#tags").append(
        "<option value='" + response.id + "'>" + response.name + "</option>"
      );

      console.log($("#createTagModal"));

      // Close the modal window
      $("#createTagModal").modal("hide");
    },
    error: function (xhr, status, error) {
      console.log("Error:", xhr.responseText);
    },
  });
}
