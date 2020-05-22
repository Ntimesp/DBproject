const queryselect = document.getElementById("quert-select");
const classname = document.getElementById("class-name");
const classcreatedate = document.getElementById("class-create-date");
const classteacher = document.getElementById("class-teacher");
const classgrade = document.getElementById("class-grade");
const classmajor = document.getElementById("class-major");

queryselect.onchange = function () {
    if (queryselect.value === "delete") {
        classname.classList.remove("display-block");
        classname.classList.add("display-none");
        classcreatedate.classList.remove("display-block");
        classcreatedate.classList.add("display-none");
        classteacher.classList.remove("display-block");
        classteacher.classList.add("display-none");
        classgrade.classList.remove("display-block");
        classgrade.classList.add("display-none");
        classmajor.classList.remove("display-block");
        classmajor.classList.add("display-none");
    } else {
        classname.classList.remove("display-none");
        classname.classList.add("display-block");
        classcreatedate.classList.remove("display-none");
        classcreatedate.classList.add("display-block");
        classteacher.classList.remove("display-none");
        classteacher.classList.add("display-block");
        classgrade.classList.remove("display-none");
        classgrade.classList.add("display-block");
        classmajor.classList.remove("display-none");
        classmajor.classList.add("display-block");
    }
}
