/**
 * Collapsible left dashboard nav (localStorage: lucus-side-dashboard-collapsed).
 */
(function () {
  "use strict";

  var KEY = "lucus-side-dashboard-collapsed";
  var ATTR = "data-lucus-side-dashboard";

  function setMode(collapsed) {
    var mode = collapsed ? "collapsed" : "expanded";
    document.documentElement.setAttribute(ATTR, mode);
    try {
      if (collapsed) {
        localStorage.setItem(KEY, "1");
      } else {
        localStorage.removeItem(KEY);
      }
    } catch (e) {}
    var aside = document.getElementById("lucus-side-dashboard");
    var col = document.getElementById("lucus-side-dashboard-collapse");
    var rev = document.getElementById("lucus-side-dashboard-reveal");
    if (aside) aside.setAttribute("aria-hidden", collapsed ? "true" : "false");
    if (col) {
      col.setAttribute("aria-expanded", collapsed ? "false" : "true");
    }
    if (rev) {
      rev.setAttribute("aria-expanded", collapsed ? "false" : "true");
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    var col = document.getElementById("lucus-side-dashboard-collapse");
    var rev = document.getElementById("lucus-side-dashboard-reveal");
    try {
      setMode(localStorage.getItem(KEY) === "1");
    } catch (e) {
      setMode(false);
    }
    if (col) {
      col.addEventListener("click", function () {
        setMode(true);
      });
    }
    if (rev) {
      rev.addEventListener("click", function () {
        setMode(false);
      });
    }
  });
})();
