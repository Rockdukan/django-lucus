(function () {
  "use strict";

  document.addEventListener("click", function (e) {
    document.querySelectorAll("details.lucus-field-help[open]").forEach(function (d) {
      if (!d.contains(e.target)) {
        d.removeAttribute("open");
      }
    });
  });
})();
