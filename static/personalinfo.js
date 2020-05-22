const queryselect = document.getElementById("quert-select");
const infotype = document.getElementById("info-type");
const infoname = document.getElementById("info-name");
const infogender = document.getElementById("info-gender");
const infobirthday = document.getElementById("info-birthday");
const infonational = document.getElementById("info-nationality");

queryselect.onchange = function () {
    if (queryselect.value === "delete") {
        infotype.classList.remove("display-block");
        infotype.classList.add("display-none");
        infoname.classList.remove("display-block");
        infoname.classList.add("display-none");
        infogender.classList.remove("display-block");
        infogender.classList.add("display-none");
        infobirthday.classList.remove("display-block");
        infobirthday.classList.add("display-none");
        infonational.classList.remove("display-block");
        infonational.classList.add("display-none");
    } else {
        infotype.classList.remove("display-none");
        infotype.classList.add("display-block");
        infoname.classList.remove("display-none");
        infoname.classList.add("display-block");
        infogender.classList.remove("display-none");
        infogender.classList.add("display-block");
        infobirthday.classList.remove("display-none");
        infobirthday.classList.add("display-block");
        infonational.classList.remove("display-none");
        infonational.classList.add("display-block");
    }
}
