(function () {
  "use strict";

  function safeGetGlobal(name) {
    try {
      return name && typeof window[name] === "function" ? window[name] : null;
    } catch (e) {
      return null;
    }
  }

  document.addEventListener("click", function (e) {
    var btn = e.target && e.target.closest ? e.target.closest("[data-lucus-pagehead-handler],[data-lucus-pagehead-action]") : null;
    if (!btn) {
      return;
    }

    var handlerName = btn.getAttribute("data-lucus-pagehead-handler") || "";
    var eventName = btn.getAttribute("data-lucus-pagehead-action") || "";

    if (handlerName) {
      var fn = safeGetGlobal(handlerName);
      if (fn) {
        fn(btn, e);
        return;
      }
    }

    if (eventName) {
      document.dispatchEvent(
        new CustomEvent("lucus:pagehead-action", {
          detail: { action: eventName, element: btn },
        })
      );
    }
  });
})();

