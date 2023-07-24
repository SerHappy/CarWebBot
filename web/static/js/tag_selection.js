document.addEventListener("DOMContentLoaded", function () {
    // Массив для хранения идентификаторов выбранных тегов
    let selectedTags = [];

    // Обработчик клика по тегу
    document.querySelectorAll('.tag-item').forEach(function (item) {
        // Проверка наличия класса 'selected' у тега
        if (item.classList.contains('selected')) {
            // Если класс 'selected' присутствует, добавьте идентификатор тега в массив
            selectedTags.push(item.getAttribute('data-id'));
        }

        item.addEventListener('click', function () {
            console.log('click on tag');
            let isSelected = item.classList.toggle('selected');
            console.log("Is tag selected: " + isSelected);
            item.querySelector('.tag-button').textContent = isSelected ? '✓' : '+';

            // Очистка массива выбранных тегов
            selectedTags = [];
            document.querySelectorAll('.tag-item.selected').forEach(function (selectedItem) {
                let tagId = selectedItem.getAttribute('data-id');
                console.log("Selected tag id: " + tagId);
                selectedTags.push(tagId);
            });
            console.log("Selected tags: " + selectedTags);
            document.getElementById('selected-tags').value = selectedTags.join(',');
        });
    });

    // Установка значения поля 'selected-tags' равным списку выбранных тегов
    document.getElementById('selected-tags').value = selectedTags.join(',');
});
