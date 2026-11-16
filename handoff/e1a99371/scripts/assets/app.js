/* Vegas Poker Trip Planner - client behaviour.
   Filtering and search operate on rows already rendered in the HTML, so every
   page works without a data fetch. */

(function () {
  "use strict";

  var TAX_RATE = 0.1338;

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }
  function money(n) {
    if (!isFinite(n)) { return "$0"; }
    return "$" + Math.round(n).toLocaleString("en-US");
  }
  function num(el, fallback) {
    var v = parseFloat(el && el.value);
    return isFinite(v) ? v : (fallback || 0);
  }

  /* ---------------- global search across every table ---------------- */

  var search = $("#siteSearch");
  var countEl = $("#searchCount");

  function runSearch() {
    if (!search) { return; }
    var q = search.value.trim().toLowerCase();
    var total = 0;
    var shown = 0;

    $$("table[data-filterable]").forEach(function (table) {
      $$("tbody tr", table).forEach(function (row) {
        total++;
        var matches = !q || row.textContent.toLowerCase().indexOf(q) !== -1;
        var filteredOut = row.dataset.searchHidden === "1";
        row.classList.toggle("hidden", !matches || filteredOut);
        if (matches && !filteredOut) { shown++; }
      });
    });

    if (countEl) {
      countEl.textContent = q
        ? shown + " of " + total + " rows"
        : (total ? total + " rows" : "");
    }
  }

  if (search) {
    search.addEventListener("input", runSearch);
    search.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") { search.value = ""; runSearch(); }
    });
  }

  function setHidden(row, hide) {
    row.dataset.searchHidden = hide ? "1" : "";
    row.classList.toggle("hidden", hide);
  }

  /* stash sort keys on event rows once, at load */
  $$("table[data-filterable] tbody tr").forEach(function (row) {
    if (!row.dataset.bucket) { return; }
    var cells = $$("td", row);
    var raw = "";
    for (var i = 0; i < cells.length; i++) {
      var t = cells[i].textContent.trim();
      if (/^\d{1,2}:\d{2}\s*(AM|PM)$/i.test(t)) { raw = t; break; }
    }
    row.dataset.start = raw;
    var m = raw.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
    if (m) {
      var h = parseInt(m[1], 10);
      var mi = parseInt(m[2], 10);
      if (/PM/i.test(m[3]) && h !== 12) { h += 12; }
      if (/AM/i.test(m[3]) && h === 12) { h = 0; }
      row.dataset.startMin = String(h * 60 + mi);
    } else {
      row.dataset.startMin = "9999";
    }
  });

  /* ---------------- event filters ---------------- */

  function applyEventFilters() {
    if (!$("#eventFilters")) { return; }
    var date = $("#fDate").value;
    var minG = parseFloat($("#fGuarantee").value) || 0;
    var maxB = parseFloat($("#fBuyin").value);
    var singleOnly = $("#fSingle").checked;
    var hideBounty = $("#fBounty").checked;
    var elig = $("#fElig") ? $("#fElig").value : "all";
    var sort = $("#fSort").value;
    var visible = 0;

    function eligibilityOk(row) {
      if (elig === "all") { return true; }
      var text = (row.dataset.eligibility || "").toLowerCase();
      var isSenior = text.indexOf("50+") !== -1;
      var isLadies = text.indexOf("female") !== -1;
      if (elig === "open") { return !isSenior && !isLadies; }
      if (elig === "senior") { return isSenior; }
      if (elig === "ladies") { return isLadies; }
      return true;
    }

    function passes(row) {
      if (date && row.dataset.date !== date) { return false; }
      if ((parseFloat(row.dataset.guarantee) || 0) < minG) { return false; }
      if (isFinite(maxB) && (parseFloat(row.dataset.buyin) || 0) > maxB) { return false; }
      if (hideBounty && row.dataset.bounty === "Yes") { return false; }
      if (!eligibilityOk(row)) { return false; }
      return true;
    }

    [$("#tblCandidates"), $("#tblMulti"), $("#tblSats"), $("#tblCont")]
      .filter(Boolean)
      .forEach(function (table) {
        var body = $("tbody", table);
        var rows = $$("tr", body);

        rows.forEach(function (row) {
          var isSingle = row.dataset.bucket === "single-entry-candidate";
          var hide = !passes(row) || (singleOnly && !isSingle);
          setHidden(row, hide);
          if (!hide) { visible++; }
        });

        rows.slice().sort(function (a, b) {
          function key(r) {
            return {
              date: r.dataset.date,
              startMin: parseInt(r.dataset.startMin, 10) || 9999,
              guarantee: -(parseFloat(r.dataset.guarantee) || 0),
              ratio: -(parseFloat(r.dataset.ratio) || 0),
              buyin: (parseFloat(r.dataset.buyin) || 0)
            };
          }
          var ka = key(a);
          var kb = key(b);
          if (sort === "date") {
            if (ka.date !== kb.date) { return ka.date < kb.date ? -1 : 1; }
            return ka.startMin - kb.startMin;
          }
          var diff = ka[sort] - kb[sort];
          if (diff !== 0) { return diff; }
          return ka.startMin - kb.startMin;
        }).forEach(function (r) { body.appendChild(r); });
      });

    var out = $("#eventCount");
    if (out) { out.textContent = visible + " event start(s) match the current filters."; }
    runSearch();
  }

  ["fDate", "fGuarantee", "fBuyin", "fSingle", "fBounty", "fElig", "fSort"].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) { el.addEventListener("change", applyEventFilters); }
  });

  if ($("#eventFilters")) { applyEventFilters(); }

  /* ---------------- hotel 30-minute walk filter ---------------- */

  var fWalk = $("#fWalk");
  if (fWalk) {
    fWalk.addEventListener("change", function () {
      var limit = fWalk.checked ? 30 : Infinity;
      $$("#tblHotels tbody tr").forEach(function (row) {
        setHidden(row, (parseFloat(row.dataset.walk) || 0) > limit);
      });
      runSearch();
    });
    fWalk.dispatchEvent(new Event("change"));
  }

  /* ---------------- per-row true cost calculator ---------------- */

  $$(".calc").forEach(function (calc) {
    var input = $("input", calc);
    var out = $("output", calc);
    if (!input || !out) { return; }
    var fee = parseFloat(calc.dataset.resortfee);

    input.addEventListener("input", function () {
      var rate = parseFloat(input.value);
      if (!isFinite(rate)) { out.textContent = "—"; out.title = ""; return; }
      var f = isFinite(fee) ? fee : 0;
      out.textContent = money((rate + f) * (1 + TAX_RATE)) + (isFinite(fee) ? "" : " *");
      out.title = isFinite(fee)
        ? "($" + rate + " rate + $" + fee + " resort fee) x 1.1338"
        : "Resort fee is unverified for this hotel, so only the rate and 13.38% tax are applied. Type the fee your quote shows.";
    });
  });

  /* ---------------- trip cost calculator ---------------- */

  var tcEvents = $("#tcEvents");
  if (tcEvents) {
    var perEvent = {};
    $$("option", tcEvents).forEach(function (o) {
      perEvent[o.value] = {
        buyIn: parseFloat(o.dataset.buyin) || 0,
        guarantee: parseFloat(o.dataset.guarantee) || 0
      };
    });

    function recalc() {
      var selected = $$("option:checked", tcEvents);
      var slateCost = selected.reduce(function (a, o) { return a + perEvent[o.value].buyIn; }, 0);
      var slateGuarantee = selected.reduce(function (a, o) { return a + perEvent[o.value].guarantee; }, 0);
      var avg = selected.length ? slateCost / selected.length : 0;

      /* "Number of entries" is the total buy-in count across the slate. */
      var entryCount = num($("#tcEntries"), selected.length);
      var entryTotal = entryCount * avg;

      var outEntries = $("#tcEntryTotal");
      if (outEntries) {
        outEntries.textContent = money(entryTotal);
        outEntries.title = selected.length
          ? entryCount + " entries x average buy-in of " + money(avg) + " across " + selected.length + " selected event(s)"
          : "Select at least one event";
      }
      var outG = $("#tcGuarantee");
      if (outG) { outG.textContent = money(slateGuarantee); }

      var rate = num($("#tcRate"), 0);
      var fee = num($("#tcFee"), 0);
      var nights = num($("#tcNights"), 0);
      var perNight = (rate + fee) * (1 + TAX_RATE);
      var roomTotal = perNight * nights;

      var outPer = $("#tcPerNight");
      if (outPer) { outPer.textContent = money(perNight); }
      var outRoom = $("#tcRoomTotal");
      if (outRoom) { outRoom.textContent = money(roomTotal); }

      var pDays = num($("#tcParkingDays"), 0);
      var freeParking = $("#tcParkingCredit").checked;
      var parkingTotal = freeParking ? 0 : num($("#tcParking"), 0) * pDays;
      var outPark = $("#tcParkingTotal");
      if (outPark) { outPark.textContent = money(parkingTotal); }
      $("#tcParking").disabled = freeParking;
      $("#tcParkingDays").disabled = freeParking;

      var outTotal = $("#tcTotal");
      if (outTotal) { outTotal.textContent = money(entryTotal + roomTotal + parkingTotal); }
      var outBreak = $("#tcBreak");
      if (outBreak) {
        outBreak.textContent =
          "entries " + money(entryTotal) +
          "  +  room " + money(roomTotal) + " (" + nights + " night" + (nights === 1 ? "" : "s") + ")" +
          "  +  parking " + money(parkingTotal);
      }
    }

    ["tcEvents", "tcEntries", "tcRate", "tcFee", "tcNights",
     "tcParking", "tcParkingDays", "tcParkingCredit"].forEach(function (id) {
      var el = document.getElementById(id);
      if (!el) { return; }
      el.addEventListener("input", recalc);
      el.addEventListener("change", recalc);
    });

    var hotelSel = $("#tcHotel");
    if (hotelSel) {
      hotelSel.addEventListener("change", function () {
        var o = hotelSel.options[hotelSel.selectedIndex];
        $("#tcFee").value = (o && o.dataset.fee) ? o.dataset.fee : "";
        recalc();
      });
      var first = hotelSel.options[hotelSel.selectedIndex];
      if (first && first.dataset.fee) { $("#tcFee").value = first.dataset.fee; }
    }
    recalc();
  }

  /* ---------------- deep links to flags and questions ---------------- */

  function openHashTarget() {
    if (!window.location.hash) { return; }
    var target = null;
    try { target = document.querySelector(window.location.hash); } catch (err) { target = null; }
    if (target && target.tagName === "DETAILS") {
      target.open = true;
      target.scrollIntoView({ block: "start" });
    }
  }
  openHashTarget();
  window.addEventListener("hashchange", openHashTarget);

  runSearch();
})();
