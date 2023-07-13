function validateInput(event) {
    var charCode = (event.which) ? event.which : event.keyCode;
    var inputValue = document.getElementById("telegramChannel").value;

    // If it's the first character and it's not "-", prevent input
    if (inputValue.length === 0 && charCode != 45) {
        return false;
    }

    // If it's not the first character and it's not a number, prevent input
    if (inputValue.length !== 0 && (charCode < 48 || charCode > 57)) {
        return false;
    }

    return true;
}
