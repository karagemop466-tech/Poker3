/* Vegas Poker Planner - shared browser behaviour.
 *
 * Everything on this site is rendered from data.json at build time, so the page
 * is readable without JavaScript. This file adds the interactive controls:
 *   - a global search that filters every table on the page at once
 *   - per-page filters: date, venue, entry-status bucket, strict-entry toggle, sort
 *   - the trip-cost calculator
 *   - the mobile navigation
 *
 * No value is computed here that is not in the published data: the calculator
 * only multiplies the published buy-in by the number of entries and the published
 * true nightly rate by the number of nights.
 */
(function () {
  "use strict";

  function $(selector, root) {
    return (root || document).querySelector(selector);
  }
  function $$(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  /* ---------------------------------------------------------------- search */
  function applySearch(query) {
    var q = (query || "").trim().toLowerCase();
    var s = state();
    $$("table.data-table").forEach(function (table) {
      $$("tbody tr", table).forEach(function (row) {
        var visible = rowMatches(row, s);
        if (visible && q) {
          visible = row.textContent.toLowerCase().indexOf(q) !== -1;
        }
        row.hidden = !visible;
      });
    });
    updateCounts();
  }

  function updateCounts() {
    $$("[data-result-count]").forEach(function (el) {
      var table = el.parentNode.querySelector("table.data-table");
      if (!table) return;
      var visible = $$("tbody tr", table).filter(function (row) {
        return !row.hidden;
      }).length;
      var total = $$("tbody tr", table).length;
      el.textContent = visible + " of " + total + " rows shown";
    });
  }

  /* --------------------------------------------------------------- filters */
  function state() {
    var out = { date: "", venue: "", bucket: "", strict: false, sort: "date" };
    var dateEl = $('[data-filter="date"]');
    var venueEl = $('[data-filter="venue"]');
    var bucketEl = $('[data-filter="bucket"]');
    var strictEl = $('[data-filter="strict-only"]');
    var sortEl = $('[data-filter="sort"]');
    if (dateEl) out.date = dateEl.value;
    if (venueEl) out.venue = venueEl.value;
    if (bucketEl) out.bucket = bucketEl.value;
    if (strictEl) out.strict = strictEl.checked;
    if (sortEl) out.sort = sortEl.value;
    return out;
  }

  function rowMatches(row, s) {
    if (s.date && row.getAttribute("data-date") !== s.date) return false;
    if (s.venue && row.getAttribute("data-venue") !== s.venue) return false;
    if (s.bucket && row.getAttribute("data-bucket") !== s.bucket) return false;
    if (s.strict && row.getAttribute("data-bucket") !== "strict") return false;
    return true;
  }

  function sortRows(table, mode) {
    var tbody = $("tbody", table);
    if (!tbody) return;
    var rows = $$("tr", tbody);
    var sorted = rows.slice().sort(function (a, b) {
      function num(attr) {
        var v = parseFloat(a.getAttribute(attr));
        return isNaN(v) ? -Infinity : v;
      }
      function numB(attr) {
        var v = parseFloat(b.getAttribute(attr));
        return isNaN(v) ? -Infinity : v;
      }
      if (mode === "buyin") return numB("data-buyin") - num("data-buyin");
      if (mode === "guarantee") return numB("data-guarantee") - num("data-guarantee");
      if (mode === "ratio") {
        var ra = parseFloat(a.getAttribute("data-cash-ratio")) || 0;
        var rb = parseFloat(b.getAttribute("data-cash-ratio")) || 0;
        return rb - ra;
      }
      var da = a.getAttribute("data-date") || "";
      var db = b.getAttribute("data-date") || "";
      if (da !== db) return da < db ? -1 : 1;
      var sa = parseInt(a.getAttribute("data-start"), 10);
      var sb = parseInt(b.getAttribute("data-start"), 10);
      if (isNaN(sa)) sa = 10 ** 6;
      if (isNaN(sb)) sb = 10 ** 6;
      return sa - sb;
    });
    sorted.forEach(function (row) {
      tbody.appendChild(row);
    });
  }

  function applyFilters() {
    var s = state();
    var search = (($("[data-search-input]") || {}).value || "").trim().toLowerCase();
    $$("table.data-table").forEach(function (table) {
      $$("tbody tr", table).forEach(function (row) {
        // A row is shown only when it passes the filters AND the search.
        var visible = rowMatches(row, s);
        if (visible && search) {
          visible = row.textContent.toLowerCase().indexOf(search) !== -1;
        }
        row.hidden = !visible;
      });
      if (s.sort) sortRows(table, s.sort);
    });
    updateCounts();
  }

  /* ------------------------------------------------------------ calculator */
  function fmtMoney(value, decimals) {
    return (
      "$" +
      Number(value || 0).toLocaleString("en-US", {
        minimumFractionDigits: decimals || 0,
        maximumFractionDigits: decimals || 0,
      })
    );
  }

  function setupCalculator() {
    var box = $("[data-calculator]");
    if (!box) return;

    var hotelSel = $('[data-calc="hotel"]', box);
    var eventSel = $('[data-calc="event"]', box);
    var entriesEl = $('[data-calc="entries"]', box);
    var parallelEl = $('[data-calc="parallel"]', box);
    var nightsEl = $('[data-calc="nights"]', box);
    var totalEl = $("[data-calc-total]", box);
    var breakdownEl = $("[data-calc-breakdown]", box);
    var warningEl = $("[data-calc-warning]", box);
    var hotelNoteEl = $("[data-calc-hotel-note]", box);

    function recompute() {
      var nights = Math.max(0, parseInt(nightsEl.value, 10) || 0);
      var entries = Math.max(0, parseInt(entriesEl.value, 10) || 0);
      var parallel = Math.max(0, parseInt(parallelEl.value, 10) || 0);
      var roomTotal = 0;
      var nightly = 0;
      var hotelName = "No hotel selected";
      if (hotelSel && hotelSel.value) {
        var option = hotelSel.options[hotelSel.selectedIndex];
        nightly = parseFloat(option.getAttribute("data-nightly")) || 0;
        hotelName = option.textContent;
        roomTotal = nightly * nights;
        if (hotelNoteEl) {
          hotelNoteEl.textContent =
            "Published true nightly cost " +
            fmtMoney(nightly, 2) +
            " (rate with resort fee plus 13.38% room tax). " +
            nights +
            (nights === 1 ? " night" : " nights") +
            ".";
        }
      } else if (hotelNoteEl) {
        hotelNoteEl.textContent = "";
      }

      var buyIn = 0;
      var entryName = "";
      if (eventSel && eventSel.value) {
        var evOption = eventSel.options[eventSel.selectedIndex];
        buyIn = parseFloat(evOption.getAttribute("data-buyin")) || 0;
        entryName = evOption.textContent;
      }
      var tournamentTotal = (entries + parallel) * buyIn;
      var total = roomTotal + tournamentTotal;

      if (totalEl) totalEl.textContent = fmtMoney(total, 2);
      if (breakdownEl) {
        var rows = [];
        rows.push(
          "<dt>Room</dt><dd>" +
            (hotelSel && hotelSel.value
              ? fmtMoney(roomTotal, 2) + " &middot; " + nights + " nights at " + fmtMoney(nightly, 2)
              : "not included") +
            "</dd>"
        );
        rows.push(
          "<dt>Tournament entries</dt><dd>" +
            (buyIn
              ? fmtMoney(tournamentTotal, 2) +
                " &middot; " +
                (entries + parallel) +
                " &times; " +
                fmtMoney(buyIn) +
                (entryName ? " &middot; " + escapeHtml(entryName) : "")
              : "no tournament selected") +
            "</dd>"
        );
        rows.push(
          "<dt>Parking, food and travel</dt><dd>not included &middot; see the Hotels page</dd>"
        );
        breakdownEl.innerHTML = rows.join("");
      }
      if (warningEl) {
        var notes = [];
        if (!buyIn) notes.push("Choose a tournament to price the entries.");
        if (!hotelSel || !hotelSel.value) notes.push("Choose a hotel to price the stay.");
        notes.push(
          "This is an estimate from published figures. The booking pages state the published rate excludes taxes, so the final folio can differ."
        );
        warningEl.textContent = notes.join(" ");
      }
    }

    if (hotelSel) hotelSel.addEventListener("change", recompute);
    if (eventSel) {
      eventSel.addEventListener("change", function () {
        var option = eventSel.options[eventSel.selectedIndex];
        var buyIn = parseFloat(option.getAttribute("data-buyin")) || 0;
        if (buyIn && entriesEl) {
          entriesEl.value = Math.max(parseInt(entriesEl.value, 10) || 0, 1);
        }
        recompute();
      });
    }
    [entriesEl, parallelEl, nightsEl].forEach(function (el) {
      if (el) el.addEventListener("input", recompute);
    });
    recompute();
  }

  function escapeHtml(text) {
    return String(text).replace(/[&<>"']/g, function (c) {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }[c];
    });
  }

  /* ------------------------------------------------------------------ init */
  function init() {
    var searchInput = $("[data-search-input]");
    if (searchInput) {
      searchInput.addEventListener("input", function () {
        applySearch(searchInput.value);
      });
    }

    $$("[data-filter]").forEach(function (el) {
      el.addEventListener("change", applyFilters);
      el.addEventListener("input", applyFilters);
    });

    var reset = $("[data-reset-filters]");
    if (reset) {
      reset.addEventListener("click", function () {
        $$("[data-filter]").forEach(function (el) {
          if (el.type === "checkbox") el.checked = false;
          else if (el.getAttribute("data-filter") === "sort") el.value = "date";
          else el.value = "";
        });
        if (searchInput) searchInput.value = "";
        applyFilters();
      });
    }

    // Keyboard shortcut: "/" focuses the global search.
    document.addEventListener("keydown", function (event) {
      if (event.key === "/" && document.activeElement !== searchInput) {
        event.preventDefault();
        if (searchInput) searchInput.focus();
      }
    });

    setupCalculator();
    applyFilters();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
