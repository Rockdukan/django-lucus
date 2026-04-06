/**
 * Replace HTML5 input types with type="text" (Grappelli-style GRAPPELLI_CLEAN_INPUT_TYPES).
 * Disables browser-native widgets/validation for a consistent admin experience.
 */
(function () {
  "use strict";

  var TYPES = [
    "search",
    "email",
    "url",
    "tel",
    "number",
    "range",
    "date",
    "month",
    "week",
    "time",
    "datetime",
    "datetime-local",
    "color",
  ];

  function cleanInputs(root) {
    if (!root || !root.querySelectorAll) {
      return;
    }
    var i;
    var j;
    for (i = 0; i < TYPES.length; i++) {
      var sel = 'input[type="' + TYPES[i] + '"]';
      var nodes = root.querySelectorAll(sel);
      for (j = 0; j < nodes.length; j++) {
        nodes[j].setAttribute("type", "text");
      }
    }
  }

  function watch(root) {
    cleanInputs(root);
    var obs = new MutationObserver(function (records) {
      var ri;
      var rj;
      for (ri = 0; ri < records.length; ri++) {
        var added = records[ri].addedNodes;
        for (rj = 0; rj < added.length; rj++) {
          var n = added[rj];
          if (n.nodeType === 1) {
            cleanInputs(n);
          }
        }
      }
    });
    obs.observe(root, { childList: true, subtree: true });
  }

  function run() {
    var root = document.getElementById("content") || document.body;
    watch(root);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", run);
  } else {
    run();
  }
})();
