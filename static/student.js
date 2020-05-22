const queryselect = document.getElementById("quert-select");
const studentpersonid = document.getElementById("student-person-id");
const studentemail = document.getElementById("student-email");
const studentclass = document.getElementById("student-class");
const studentmajor = document.getElementById("student-major");
const studentenrollment = document.getElementById("student-enrollment");

queryselect.onchange = function () {
    if (queryselect.value === "delete") {
        studentpersonid.classList.remove("display-block");
        studentpersonid.classList.add("display-none");
        studentemail.classList.remove("display-block");
        studentemail.classList.add("display-none");
        studentclass.classList.remove("display-block");
        studentclass.classList.add("display-none");
        studentmajor.classList.remove("display-block");
        studentmajor.classList.add("display-none");
        studentenrollment.classList.remove("display-block");
        studentenrollment.classList.add("display-none");
    } else {
        studentpersonid.classList.remove("display-none");
        studentpersonid.classList.add("display-block");
        studentemail.classList.remove("display-none");
        studentemail.classList.add("display-block");
        studentclass.classList.remove("display-none");
        studentclass.classList.add("display-block");
        studentmajor.classList.remove("display-none");
        studentmajor.classList.add("display-block");
        studentenrollment.classList.remove("display-none");
        studentenrollment.classList.add("display-block");
    }
}
