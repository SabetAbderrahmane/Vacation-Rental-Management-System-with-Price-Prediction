// Vacation Rental System — Main JavaScript
// Phase 4: Small UI helpers only — no business logic

document.addEventListener("DOMContentLoaded", function () {

    // 1. Confirmation dialog for delete/cancel actions
    //    Usage: <button data-confirm="Are you sure?">Delete</button>
    document.querySelectorAll("[data-confirm]").forEach(function (el) {
        el.addEventListener("click", function (e) {
            if (!confirm(el.getAttribute("data-confirm"))) {
                e.preventDefault();
            }
        });
    });

    // 2. Auto-hide flash messages after 6 seconds
    document.querySelectorAll(".alert").forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = "opacity .4s";
            alert.style.opacity = "0";
            setTimeout(function () { alert.remove(); }, 400);
        }, 6000);
    });

});
