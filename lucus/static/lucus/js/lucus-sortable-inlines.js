/**
 * Tabular inline drag-reorder: updates the ordering field (sortable_field_name)
 * on drag and before form submit. Expects markup from lucus tabular inline template.
 */
(function () {
  "use strict";

  var dragState = null;

  function parseExcludes(s) {
    if (!s) return [];
    return s
      .split(",")
      .map(function (x) {
        return x.trim();
      })
      .filter(Boolean);
  }

  function rowDeleted(tr) {
    var cb = tr.querySelector('input[type="checkbox"][name*="-DELETE"]');
    return !!(cb && cb.checked);
  }

  function rowHasValue(tr, prefix, field, excludes) {
    var excludeSet = {};
    var i;
    for (i = 0; i < excludes.length; i++) excludeSet[excludes[i]] = true;
    var inputs = tr.querySelectorAll("input, select, textarea");
    for (i = 0; i < inputs.length; i++) {
      var el = inputs[i];
      var name = el.name || "";
      var marker = prefix + "-";
      var idx = name.indexOf(marker);
      if (idx === -1) continue;
      var rest = name.slice(idx + marker.length);
      var lastDash = rest.lastIndexOf("-");
      if (lastDash === -1) continue;
      var fname = rest.slice(lastDash + 1);
      if (fname === field || fname === "DELETE" || fname === "id") continue;
      if (excludeSet[fname]) continue;
      if (el.type === "hidden") continue;
      if (el.disabled) continue;
      if (el.type === "checkbox" || el.type === "radio") {
        if (el.checked) return true;
        continue;
      }
      var v = (el.value || "").trim();
      if (v) return true;
      if (el.type === "file") return true;
    }
    return false;
  }

  function ensureEmptyLast(tbody) {
    var empty = tbody.querySelector("tr.form-row.empty-form");
    if (empty) tbody.appendChild(empty);
  }

  function reindexPositions(group) {
    var prefix = group.getAttribute("data-lucus-sortable-prefix");
    var field = group.getAttribute("data-lucus-sortable-field");
    var excludes = parseExcludes(
      group.getAttribute("data-lucus-sortable-excludes") || ""
    );
    var tbody = group.querySelector("tbody");
    if (!tbody || !prefix || !field) return;

    var rows = [].slice.call(tbody.querySelectorAll("tr.form-row"));
    var j = 0;
    var r;
    for (r = 0; r < rows.length; r++) {
      var tr = rows[r];
      if (tr.classList.contains("empty-form")) continue;
      if (rowDeleted(tr)) continue;
      if (!rowHasValue(tr, prefix, field, excludes)) continue;
      var inp = tr.querySelector('input[name$="-' + field + '"]');
      if (inp) inp.value = String(j++);
    }
    for (r = 0; r < rows.length; r++) {
      tr = rows[r];
      if (tr.classList.contains("empty-form")) continue;
      if (rowDeleted(tr)) continue;
      if (rowHasValue(tr, prefix, field, excludes)) continue;
      inp = tr.querySelector('input[name$="-' + field + '"]');
      if (inp) inp.value = "";
    }
    ensureEmptyLast(tbody);
  }

  function initAll() {
    document.querySelectorAll("[data-lucus-sortable]").forEach(reindexPositions);
  }

  document.addEventListener(
    "dragstart",
    function (e) {
      var h = e.target.closest && e.target.closest(".lucus-inline-drag-handle");
      if (!h) return;
      var tr = h.closest("tr.form-row");
      if (!tr || tr.classList.contains("empty-form")) {
        e.preventDefault();
        return;
      }
      var group = tr.closest("[data-lucus-sortable]");
      if (!group) return;
      dragState = { tr: tr, group: group };
      tr.classList.add("lucus-inline-dragging");
      try {
        e.dataTransfer.setData("text/plain", "lucus-sort");
        e.dataTransfer.effectAllowed = "move";
      } catch (err) {}
    },
    true
  );

  document.addEventListener(
    "dragend",
    function () {
      if (dragState && dragState.tr) {
        dragState.tr.classList.remove("lucus-inline-dragging");
        if (dragState.group) reindexPositions(dragState.group);
      }
      dragState = null;
    },
    true
  );

  document.addEventListener(
    "dragover",
    function (e) {
      if (!dragState) return;
      var tr = e.target.closest && e.target.closest("tbody tr.form-row");
      if (!tr || !dragState.group.contains(tr)) return;
      if (tr === dragState.tr) return;
      e.preventDefault();
      e.dataTransfer.dropEffect = "move";
      var tbody = tr.parentNode;
      if (tr.classList.contains("empty-form")) {
        tbody.insertBefore(dragState.tr, tr);
      } else {
        var rect = tr.getBoundingClientRect();
        var afterMid = e.clientY > rect.top + rect.height / 2;
        if (afterMid) {
          tbody.insertBefore(dragState.tr, tr.nextSibling);
        } else {
          tbody.insertBefore(dragState.tr, tr);
        }
      }
      ensureEmptyLast(tbody);
    },
    true
  );

  document.addEventListener(
    "drop",
    function (e) {
      if (dragState) e.preventDefault();
    },
    true
  );

  document.addEventListener("DOMContentLoaded", initAll);

  document.addEventListener("formset:added", function (ev) {
    var t = ev.target;
    if (!t || !t.closest) return;
    var g = t.closest("[data-lucus-sortable]");
    if (!g) return;
    reindexPositions(g);
    var tbody = g.querySelector("tbody");
    if (tbody) ensureEmptyLast(tbody);
  });

  document.addEventListener(
    "submit",
    function (e) {
      var form = e.target;
      if (!form || form.tagName !== "FORM") return;
      var nodes = form.querySelectorAll("[data-lucus-sortable]");
      var i;
      for (i = 0; i < nodes.length; i++) reindexPositions(nodes[i]);
    },
    true
  );
})();
