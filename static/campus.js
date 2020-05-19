const queryselect = document.getElementById("quert-select");
const campusid = document.getElementById("campus-id");
const campusname = document.getElementById("campus-name");
const campusaddr = document.getElementById("campus-addr");

queryselect.onchange = function () {
    if (queryselect.value === "delete") {
        campusname.classList.remove("display-block");
        campusname.classList.add("display-none");
        campusaddr.classList.remove("display-block");
        campusaddr.classList.add("display-none");
    } else {
        campusname.classList.remove("display-none");
        campusname.classList.add("display-block");
        campusaddr.classList.remove("display-none");
        campusaddr.classList.add("display-block");
    }
}
