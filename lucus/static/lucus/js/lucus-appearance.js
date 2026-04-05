/**
 * When data-lucus-appearance="auto", keep data-theme in sync with prefers-color-scheme.
 * For light/dark, the server sets data-theme on <html>; this file is only needed for auto.
 */
(function () {
  function sync() {
    var root = document.documentElement;
    if (root.getAttribute("data-lucus-appearance") !== "auto") {
      return;
    }
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    function apply() {
      root.setAttribute("data-theme", mq.matches ? "dark" : "light");
    }
    apply();
    mq.addEventListener("change", apply);
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", sync);
  } else {
    sync();
  }
})();
