const queryselect = document.getElementById("quert-select");
const majorname = document.getElementById("major-name");
const majoraddr = document.getElementById("major-addr");
const majorcampus = document.getElementById("major-campus");
const majorleader = document.getElementById("major-leader");

queryselect.onchange = function () {
    if (queryselect.value === "delete") {
        majorname.classList.remove("display-block");
        majorname.classList.add("display-none");
        majoraddr.classList.remove("display-block");
        majoraddr.classList.add("display-none");
        majorcampus.classList.remove("display-block");
        majorcampus.classList.add("display-none");
        majorleader.classList.remove("display-block");
        majorleader.classList.add("display-none");
    } else {
        majorname.classList.remove("display-none");
        majorname.classList.add("display-block");
        majoraddr.classList.remove("display-none");
        majoraddr.classList.add("display-block");
        majorcampus.classList.remove("display-none");
        majorcampus.classList.add("display-block");
        majorleader.classList.remove("display-none");
        majorleader.classList.add("display-block");
    }
}
