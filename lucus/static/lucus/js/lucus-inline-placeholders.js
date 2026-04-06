/**
 * Move inline groups into placeholder fieldsets (classes: "placeholder" + "<prefix>-group").
 */
(function () {
  "use strict";

  function groupIdFromFieldset(fs) {
    var idClass = null;
    fs.classList.forEach(function (c) {
      if (
        c !== "module" &&
        c !== "aligned" &&
        c !== "placeholder" &&
        c.endsWith("-group")
      ) {
        idClass = c;
      }
    });
    return idClass;
  }

  function moveInlines() {
    document.querySelectorAll("fieldset.module.placeholder").forEach(function (fs) {
      var idClass = groupIdFromFieldset(fs);
      if (!idClass) return;
      var node = document.getElementById(idClass);
      if (!node || !fs.parentNode) return;
      fs.parentNode.insertBefore(node, fs);
      fs.parentNode.removeChild(fs);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", moveInlines);
  } else {
    moveInlines();
  }
})();
