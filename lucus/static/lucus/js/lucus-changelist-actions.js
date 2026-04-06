'use strict';
/**
 * Lucus changelist: visible "clear page selection" control and counter sync.
 * Relies on Django admin actions.js (interpolate, ngettext, gettext globals).
 */
(function () {
  function ready(fn) {
    if (document.readyState !== 'loading') {
      fn();
    } else {
      document.addEventListener('DOMContentLoaded', fn);
    }
  }

  ready(function () {
    var form = document.getElementById('changelist-form');
    var resultList = document.getElementById('result_list');
    var counter = document.querySelector('span.action-counter');
    var clearBtn = document.querySelector('.lucus-changelist-actions__deselect');
    if (
      !form ||
      !resultList ||
      !counter ||
      !clearBtn ||
      typeof window.interpolate !== 'function' ||
      typeof window.ngettext !== 'function'
    ) {
      return;
    }

    var actionCheckboxes = function () {
      return Array.prototype.slice.call(
        document.querySelectorAll('tr input.action-select')
      );
    };

    var options = {
      actionContainer: 'div.actions',
      counterContainer: 'span.action-counter',
      allContainer: 'div.actions span.all',
      acrossInput: 'div.actions input.select-across',
      acrossQuestions: 'div.actions span.question',
      acrossClears: 'div.actions span.clear',
      allToggleId: 'action-toggle',
      selectedClass: 'selected',
    };

    function hide(selector) {
      document.querySelectorAll(selector).forEach(function (el) {
        el.classList.add('hidden');
      });
    }

    function show(selector) {
      document.querySelectorAll(selector).forEach(function (el) {
        el.classList.remove('hidden');
      });
    }

    function clearAcross() {
      hide(options.acrossClears);
      hide(options.acrossQuestions);
      hide(options.allContainer);
      show(options.counterContainer);
      document.querySelectorAll(options.acrossInput).forEach(function (inp) {
        inp.value = 0;
      });
      var ac = document.querySelector(options.actionContainer);
      if (ac) {
        ac.classList.remove(options.selectedClass);
      }
    }

    function updateCounter() {
      var boxes = actionCheckboxes();
      var sel = boxes.filter(function (el) {
        return el.checked;
      }).length;
      var actionsIcnt = Number(counter.dataset.actionsIcnt || 0);
      counter.textContent = interpolate(
        ngettext(
          '%(sel)s of %(cnt)s selected',
          '%(sel)s of %(cnt)s selected',
          sel
        ),
        { sel: sel, cnt: actionsIcnt },
        true
      );
      var allToggle = document.getElementById(options.allToggleId);
      if (allToggle) {
        allToggle.checked = sel === boxes.length && boxes.length > 0;
      }
      clearBtn.hidden = sel === 0 && (!allToggle || !allToggle.checked);
      if (allToggle && allToggle.checked) {
        clearBtn.hidden = false;
      }
    }

    clearBtn.addEventListener('click', function () {
      var allToggle = document.getElementById(options.allToggleId);
      if (allToggle) {
        allToggle.checked = false;
      }
      clearAcross();
      actionCheckboxes().forEach(function (el) {
        el.checked = false;
        var tr = el.closest('tr');
        if (tr) {
          tr.classList.remove(options.selectedClass);
        }
      });
      updateCounter();
    });

    resultList.addEventListener('change', function (ev) {
      if (ev.target && ev.target.classList.contains('action-select')) {
        window.setTimeout(updateCounter, 0);
      }
    });

    var allToggle = document.getElementById(options.allToggleId);
    if (allToggle) {
      allToggle.addEventListener('click', function () {
        window.setTimeout(updateCounter, 0);
      });
    }

    window.addEventListener('pageshow', updateCounter);
    updateCounter();
  });
})();
