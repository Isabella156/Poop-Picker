$(document).ready(function() {
    // Add active class on tab click
    $(".tab").on("click", function() {
        var categoryId = $(this).data("id");

        $(".tab, .tab-pane").removeClass("active");
        $(this).addClass("active");
        $("#" + categoryId).addClass("active");
    });
});


$("i").click(function() {
    $("ul").toggleClass("open");
});



let modalBtns = [...document.querySelectorAll(".button")];
modalBtns.forEach(function(btn) {
    btn.onclick = function() {
        let modal = btn.getAttribute('data-modal');
        document.getElementById(modal)
            .style.display = "block";
    }
});
let closeBtns = [...document.querySelectorAll(".close")];
closeBtns.forEach(function(btn) {
    btn.onclick = function() {
        let modal = btn.closest('.modal');
        modal.style.display = "none";
    }
});
window.onclick = function(event) {
    if (event.target.className === "modal") {
        event.target.style.display = "none";
    }
}