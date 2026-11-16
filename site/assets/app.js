/* Vegas Poker Planner — search, filters, trip calculator */
(function () {
  "use strict";

  function allTables() { return Array.prototype.slice.call(document.querySelectorAll("main table")); }

  // ---- generic search box: filters every table on the page ----
  function wireSearch(inputId) {
    var input = document.getElementById(inputId);
    if (!input) return;
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      allTables().forEach(function (tbl) {
        Array.prototype.forEach.call(tbl.tBodies[0].rows, function (row) {
          var hit = !q || row.textContent.toLowerCase().indexOf(q) !== -1;
          row.style.display = hit ? "" : "none";
        });
      });
    });
  }
  ["tSearch", "hSearch", "rSearch"].forEach(wireSearch);

  // ---- tournaments filters ----
  var tTable = document.getElementById("tTable");
  if (tTable) {
    var dateEl = document.getElementById("tDate");
    var venueEl = document.getElementById("tVenue");
    var bucketEl = document.getElementById("tBucket");
    var confEl = document.getElementById("tConfirmed");
    var apply = function () {
      var d = dateEl && dateEl.value ? dateEl.value : "";
      var v = venueEl ? venueEl.value : "";
      var b = bucketEl ? bucketEl.value : "";
      var confOnly = confEl && confEl.checked;
      Array.prototype.forEach.call(tTable.tBodies[0].rows, function (row) {
        var meta = row.querySelector("[data-bucket]");
        if (!meta) return;
        var ok = true;
        if (d && meta.getAttribute("data-date") !== d) ok = false;
        if (v && meta.getAttribute("data-venue") !== v) ok = false;
        if (b === "single-path" && meta.getAttribute("data-bucket") !== "single-path") ok = false;
        if (b === "spend-more" && meta.getAttribute("data-bucket") !== "spend-more") ok = false;
        if (b === "satellite" && meta.getAttribute("data-bucket") !== "satellite") ok = false;
        if (b === "review" && meta.getAttribute("data-bucket") !== "review") ok = false;
        if (confOnly && meta.getAttribute("data-verified") !== "verified") ok = false;
        row.style.display = ok ? "" : "none";
      });
    };
    [dateEl, venueEl, bucketEl, confEl].forEach(function (el) {
      if (el) el.addEventListener("change", apply);
    });
    var reset = document.getElementById("tReset");
    if (reset) reset.addEventListener("click", function () {
      if (dateEl) dateEl.value = "";
      if (venueEl) venueEl.value = "";
      if (bucketEl) bucketEl.value = "";
      if (confEl) confEl.checked = false;
      var s = document.getElementById("tSearch");
      if (s) { s.value = ""; s.dispatchEvent(new Event("input")); }
      apply();
    });
  }

  // ---- routes: ≤30 filter ----
  var rTable = document.getElementById("rTable");
  if (rTable) {
    var r30 = document.getElementById("r30");
    if (r30) r30.addEventListener("change", function () {
      Array.prototype.forEach.call(rTable.tBodies[0].rows, function (row) {
        var m = row.querySelector("[data-within30]");
        if (!m) return;
        var val = m.getAttribute("data-within30"); // "true" | "false" | "unknown"
        row.style.display = (!r30.checked || val === "true") ? "" : "none";
      });
    });
  }

  // ---- hotels: ≤30 (on-site or verified) filter ----
  var hTable = document.getElementById("hTable");
  if (hTable) {
    var h30 = document.getElementById("h30");
    if (h30) h30.addEventListener("change", function () {
      Array.prototype.forEach.call(hTable.tBodies[0].rows, function (row) {
        var m = row.querySelector("[data-within30]");
        if (!m) return;
        row.style.display = (!h30.checked || m.getAttribute("data-within30") === "true") ? "" : "none";
      });
    });
  }

  // ---- trip calculator ----
  var cAdd = document.getElementById("cAdd");
  if (cAdd) {
    var entries = [];
    var entryList = document.getElementById("cEntryList");
    var entryTotal = document.getElementById("cEntryTotal");
    var hotelSel = document.getElementById("cHotel");
    var nightsEl = document.getElementById("cNights");
    var rateEl = document.getElementById("cRate");
    var feeEl = document.getElementById("cFee");
    var taxFeeEl = document.getElementById("cTaxFee");
    var parkingEl = document.getElementById("cParking");
    var trueNightlyEl = document.getElementById("cTrueNightly");
    var stayTotalEl = document.getElementById("cStayTotal");
    var grandEl = document.getElementById("cGrand");
    var breakdownEl = document.getElementById("cBreakdown");
    var TAX = 0.1338;

    function fmt(n) { return "$" + n.toLocaleString("en-US", { maximumFractionDigits: 0 }); }

    function recalc() {
      var entrySum = entries.reduce(function (s, e) { return s + e.buyin * e.count; }, 0);
      entryTotal.textContent = fmt(entrySum);

      var nights = Math.max(1, parseInt(nightsEl.value || "1", 10));
      var rate = parseFloat(rateEl.value);
      var fee = parseFloat(feeEl.value || "0") || 0;
      var hasRate = !isNaN(rate);
      var taxBase = hasRate ? rate + fee : 0;
      if (!taxFeeEl.checked) taxBase = hasRate ? rate : 0;
      var tax = taxBase * TAX;
      var trueNightly = hasRate ? (rate + fee + tax) : null;
      var parking = parkingEl.checked ? 20 * nights : 0;

      trueNightlyEl.textContent = trueNightly !== null ? fmt(trueNightly) : "— (rate blank)";
      var stay = trueNightly !== null ? trueNightly * nights + parking : null;
      stayTotalEl.textContent = stay !== null ? fmt(stay) : "— (rate blank)";

      if (trueNightly !== null) {
        grandEl.textContent = fmt(entrySum + stay);
        breakdownEl.textContent =
          "Entries " + fmt(entrySum) + " + " + nights + " nights × " + fmt(trueNightly) +
          " true nightly" + (parking ? " + " + fmt(parking) + " parking" : "") +
          " = " + fmt(entrySum + stay) + ".";
      } else {
        grandEl.textContent = fmt(entrySum) + " + stay (rate blank)";
        breakdownEl.textContent =
          "PARTIAL TOTAL: entries " + fmt(entrySum) + " confirmed; stay cannot be computed until a dated nightly rate is entered (FL09). " +
          "Resort fee and 13.38% tax are verified; the room rate is not.";
      }
    }

    function renderEntries() {
      entryList.innerHTML = "";
      entries.forEach(function (e, i) {
        var li = document.createElement("li");
        li.textContent = e.count + " × " + e.name + " @ " + fmt(e.buyin) + " = " + fmt(e.buyin * e.count) + " ";
        var del = document.createElement("button");
        del.type = "button";
        del.textContent = "remove";
        del.addEventListener("click", function () { entries.splice(i, 1); renderEntries(); recalc(); });
        li.appendChild(del);
        entryList.appendChild(li);
      });
      recalc();
    }

    cAdd.addEventListener("click", function () {
      var input = document.getElementById("cEvent");
      var count = Math.max(0, parseInt(document.getElementById("cEntries").value || "1", 10));
      var chosen = null;
      var val = input.value.trim().toLowerCase();
      if (val) {
        var opts = document.querySelectorAll("#eventList option");
        Array.prototype.forEach.call(opts, function (o) {
          if (!chosen && (o.value.toLowerCase().indexOf(val) !== -1 || o.getAttribute("data-name").toLowerCase().indexOf(val) !== -1)) {
            chosen = o;
          }
        });
      }
      if (!chosen) {
        breakdownEl.textContent = "Pick an event from the list first (type part of its name or date).";
        return;
      }
      entries.push({
        name: chosen.getAttribute("data-name"),
        buyin: parseFloat(chosen.getAttribute("data-buyin")) || 0,
        count: count || 1
      });
      input.value = "";
      renderEntries();
    });

    hotelSel.addEventListener("change", function () {
      var fee = hotelSel.selectedOptions[0].getAttribute("data-fee");
      if (fee) feeEl.value = fee;
      recalc();
    });
    [nightsEl, rateEl, feeEl, taxFeeEl, parkingEl].forEach(function (el) {
      el.addEventListener("input", recalc);
      el.addEventListener("change", recalc);
    });
    recalc();
  }
})();
