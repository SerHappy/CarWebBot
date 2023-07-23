document.querySelectorAll('.tag-item').forEach(function (item) {
    item.addEventListener('click', function () {
        console.log('click on tag');
        let isSelected = item.classList.toggle('selected');
        console.log("Is tag selected: " + isSelected);
        item.querySelector('.tag-button').textContent = isSelected ? '✓' : '+';

        let selectedTags = [];
        document.querySelectorAll('.tag-item.selected').forEach(function (selectedItem) {
            let tagId = selectedItem.getAttribute('data-id');
            console.log("Selected tag id: " + tagId);
            selectedTags.push(tagId);
        });
        console.log("Selected tags: " + selectedTags);
        document.getElementById('selected-tags').value = selectedTags.join(',');
    });
});
