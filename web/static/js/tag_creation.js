function createTag() {
  var formData = $("#createTagForm").serialize();
  console.log("Form Data:", formData);

  $.ajax({
    type: "POST",
    url: "/tags/add/",
    data: formData,
    success: function (response) {
      console.log("Success response:", response);

      // Update the list of tags
      console.log("Tag ID:", response.tag_id);
      console.log("Tag Name:", response.tag_name);

      $("#tags").append(
    $("<option>")
      .attr("value", response.tag_id)
      .text(response.tag_name)
  );

      // Close the modal window
      $("#createTagModal").modal("hide");
    },
    error: function (xhr, status, error) {
    console.log("Error:", xhr.responseText);
    if (xhr.responseJSON) {
        alert(xhr.responseJSON.error);
    } else {
        alert('An unknown error occurred.');
    }
},

  });
}
