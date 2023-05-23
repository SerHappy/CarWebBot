$(".select2bs4").select2({
  theme: "bootstrap4",
});
$("#reservationdatetime").datetimepicker({
  icons: { time: "far fa-clock" },
});
// Получение текущей даты и времени
var currentDate = new Date();

// Функция для форматирования чисел с добавлением ведущего нуля
function addLeadingZero(number) {
  return number < 10 ? "0" + number : number;
}

// Форматирование даты и времени в нужном формате
var currentDateTime =
  addLeadingZero(currentDate.getDate()) +
  "." +
  addLeadingZero(currentDate.getMonth() + 1) +
  "." +
  currentDate.getFullYear() +
  " " +
  addLeadingZero(currentDate.getHours()) +
  ":" +
  addLeadingZero(currentDate.getMinutes());

// Установка текущего времени в поле ввода
$("#publication_date").val(currentDateTime);
