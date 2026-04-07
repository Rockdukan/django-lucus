/**
 * Off-canvas admin nav (≤900px): side dashboard or fallback panel (available_apps).
 * Backdrop sits below the sticky header so the toggle stays visible.
 */
(function () {
  "use strict";

  var MOBILE_MAX = 900;
  var OPEN_CLASS = "lucus-admin--mobile-nav-open";
  var LOCK_CLASS = "lucus-admin--scroll-lock";

  function isMobile() {
    return window.innerWidth <= MOBILE_MAX;
  }

  function getPanel() {
    return (
      document.getElementById("lucus-side-dashboard") ||
      document.getElementById("lucus-mobile-nav-panel")
    );
  }

  function closeNav() {
    document.body.classList.remove(OPEN_CLASS, LOCK_CLASS);
    var t = document.getElementById("lucus-admin-nav-toggle");
    if (t) {
      t.setAttribute("aria-expanded", "false");
    }
    var panel = getPanel();
    if (panel) {
      panel.setAttribute("aria-hidden", "true");
    }
  }

  function openNav() {
    if (!isMobile()) {
      return;
    }
    document.body.classList.add(OPEN_CLASS, LOCK_CLASS);
    var t = document.getElementById("lucus-admin-nav-toggle");
    if (t) {
      t.setAttribute("aria-expanded", "true");
    }
    var panel = getPanel();
    if (panel) {
      panel.setAttribute("aria-hidden", "false");
    }
  }

  function toggleNav() {
    if (!isMobile()) {
      return;
    }
    if (document.body.classList.contains(OPEN_CLASS)) {
      closeNav();
    } else {
      openNav();
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.getElementById("lucus-admin-nav-toggle");
    var backdrop = document.getElementById("lucus-mobile-nav-backdrop");
    var panel = getPanel();

    if (!toggle || !panel) {
      return;
    }

    panel.setAttribute("aria-hidden", "true");

    toggle.addEventListener("click", function (e) {
      e.preventDefault();
      toggleNav();
    });

    toggle.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        toggleNav();
      }
    });

    if (backdrop) {
      backdrop.addEventListener("click", function () {
        closeNav();
      });
    }

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && document.body.classList.contains(OPEN_CLASS)) {
        closeNav();
        toggle.focus();
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > MOBILE_MAX) {
        closeNav();
      }
    });

    panel.addEventListener("click", function (e) {
      if (!isMobile() || !document.body.classList.contains(OPEN_CLASS)) {
        return;
      }
      if (
        e.target.closest(".lucus-side-dashboard__link") ||
        e.target.closest(".lucus-mobile-nav-panel__link")
      ) {
        closeNav();
      }
    });
  });
})();
