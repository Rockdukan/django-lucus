/**
 * Lucus admin UI: high contrast (localStorage + data-lucus-contrast on <html>).
 */
(function () {
  "use strict";

  var STORAGE_KEY = "lucus-high-contrast";

  function applyContrast(on) {
    var root = document.documentElement;
    if (on) {
      root.setAttribute("data-lucus-contrast", "high");
    } else {
      root.removeAttribute("data-lucus-contrast");
    }
  }

  function readStored() {
    try {
      return localStorage.getItem(STORAGE_KEY) === "1";
    } catch (e) {
      return false;
    }
  }

  function writeStored(on) {
    try {
      if (on) {
        localStorage.setItem(STORAGE_KEY, "1");
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }
    } catch (e) {}
  }

  applyContrast(readStored());

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("lucus-high-contrast-toggle");
    if (!btn) {
      return;
    }
    function syncLabel() {
      var on = document.documentElement.getAttribute("data-lucus-contrast") === "high";
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    }
    syncLabel();
    btn.addEventListener("click", function () {
      var on = document.documentElement.getAttribute("data-lucus-contrast") === "high";
      var next = !on;
      writeStored(next);
      applyContrast(next);
      syncLabel();
    });
  });
})();
