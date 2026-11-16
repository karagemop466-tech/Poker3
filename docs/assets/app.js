/* Poker Strip Dashboard — renders static JSON data as sortable, searchable tables.
   No external libraries. Every row shows its source link (from data/sources.json). */
(function () {
  "use strict";

  var SRC = {};
  var NAV = [
    ["index.html", "Home"],
    ["tournaments.html", "Single-entry"],
    ["multi-entry.html", "Excluded"],
    ["schedule.html", "Schedule"],
    ["hotels.html", "Hotels"],
    ["summary.html", "Summary"],
    ["questions.html", "Q&A"],
    ["suggestions.html", "Suggestions"],
    ["flagged.html", "Flagged for Review"],
    ["sources.html", "Sources"]
  ];

  function esc(s) {
    return String(s === null || s === undefined ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function money(v) {
    if (v === null || v === undefined || v === "") return "";
    return "$" + Number(v).toLocaleString("en-US");
  }
  function fmtDate(iso) {
    if (!iso) return "";
    var p = iso.split("-");
    var d = new Date(Date.UTC(+p[0], +p[1] - 1, +p[2]));
    return d.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", year: "numeric", timeZone: "UTC" });
  }
  function fmtTime(hhmm) {
    if (!hhmm) return "";
    var p = hhmm.split(":"), h = +p[0], m = p[1];
    var ap = h >= 12 ? "PM" : "AM";
    var h12 = h % 12 === 0 ? 12 : h % 12;
    return h12 + ":" + m + " " + ap;
  }
  function load(path) {
    return fetch(path, { cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error("Failed to load " + path + " (" + r.status + ")");
      return r.json();
    });
  }
  function loadSources() {
    return load("data/sources.json").then(function (arr) {
      arr.forEach(function (s) { SRC[s.id] = s; });
      return SRC;
    });
  }
  function srcLink(id) {
    var s = SRC[id];
    if (!s) return '<span class="unv">no source</span>';
    return '<a href="' + esc(s.url) + '" target="_blank" rel="noopener" title="' + esc(s.title) + '">' + esc(s.org) + "</a>";
  }
  function srcLinks(ids) {
    if (!ids || !ids.length) return '<span class="unv">no source</span>';
    return ids.map(srcLink).join("<br>");
  }
  function flagTags(ids) {
    if (!ids || !ids.length) return "";
    return ids.map(function (f) { return '<a class="tag" href="flagged.html#' + esc(f) + '">' + esc(f) + "</a>"; }).join("");
  }
  function entryBadge(st) {
    if (st === "structure") return '<span class="badge ok">Structure checked</span>';
    if (st === "recurring") return '<span class="badge warn">Recurring, undated</span>';
    if (st === "pending") return '<span class="badge gray">Pending check</span>';
    return esc(st);
  }
  function unv(label) {
    return '<span class="unv">UNVERIFIED' + (label ? " " + esc(label) : "") + "</span>";
  }

  function renderNav(active) {
    var host = document.getElementById("nav");
    if (!host) return;
    host.innerHTML = NAV.map(function (n) {
      return '<a href="' + n[0] + '"' + (n[0] === active ? ' class="on"' : "") + ">" + esc(n[1]) + "</a>";
    }).join("");
  }

  /* Generic table: cols = [{label, val(row) -> sortable, html(row) -> HTML, num:bool}] */
  function table(host, cols, rows, opts) {
    opts = opts || {};
    var state = { q: "", sort: -1, asc: true, filters: {} };
    var tb = document.createElement("div");
    tb.className = "toolbar";
    var search = document.createElement("input");
    search.type = "search";
    search.placeholder = opts.searchPlaceholder || "Search this table…";
    tb.appendChild(search);
    var selects = [];
    (opts.filters || []).forEach(function (f) {
      var sel = document.createElement("select");
      var values = {};
      rows.forEach(function (r) { var v = f.get(r); if (v) values[v] = true; });
      sel.innerHTML = '<option value="">' + esc(f.label) + " (all)</option>" +
        Object.keys(values).sort().map(function (v) { return '<option value="' + esc(v) + '">' + esc(v) + "</option>"; }).join("");
      sel.addEventListener("change", function () { state.filters[f.label] = sel.value; draw(); });
      tb.appendChild(sel);
      selects.push(sel);
    });
    var count = document.createElement("span");
    count.className = "count";
    tb.appendChild(count);
    var wrap = document.createElement("div");
    wrap.className = "table-wrap";
    var t = document.createElement("table");
    var thead = document.createElement("thead");
    var tr = document.createElement("tr");
    cols.forEach(function (c, i) {
      var th = document.createElement("th");
      th.textContent = c.label;
      if (c.num) th.className = "num";
      th.addEventListener("click", function () {
        if (state.sort === i) state.asc = !state.asc; else { state.sort = i; state.asc = true; }
        draw();
      });
      tr.appendChild(th);
    });
    thead.appendChild(tr);
    t.appendChild(thead);
    var tbody = document.createElement("tbody");
    t.appendChild(tbody);
    wrap.appendChild(t);
    host.innerHTML = "";
    host.appendChild(tb);
    host.appendChild(wrap);

    search.addEventListener("input", function () { state.q = search.value.toLowerCase(); draw(); });

    function draw() {
      var data = rows.filter(function (r) {
        for (var k in state.filters) {
          var f = (opts.filters || []).filter(function (x) { return x.label === k; })[0];
          if (f && state.filters[k] && f.get(r) !== state.filters[k]) return false;
        }
        if (!state.q) return true;
        return cols.some(function (c) {
          var v = c.val ? c.val(r) : "";
          return String(v === null || v === undefined ? "" : v).toLowerCase().indexOf(state.q) !== -1;
        });
      });
      if (state.sort >= 0) {
        var c = cols[state.sort];
        data = data.slice().sort(function (a, b) {
          var x = c.val ? c.val(a) : "", y = c.val ? c.val(b) : "";
          var nx = typeof x === "number", ny = typeof y === "number";
          if (x === null || x === undefined || x === "") return 1;
          if (y === null || y === undefined || y === "") return -1;
          var r = nx && ny ? x - y : String(x).localeCompare(String(y));
          return state.asc ? r : -r;
        });
      }
      Array.prototype.forEach.call(thead.querySelectorAll("th"), function (th, i) {
        th.className = (c0(th) ? "" : "") + (i === state.sort ? " sorted" + (state.asc ? "" : " desc") : "") + (cols[i].num ? " num" : "");
      });
      tbody.innerHTML = data.map(function (r) {
        return "<tr>" + cols.map(function (c) {
          return "<td" + (c.num ? ' class="num"' : "") + ">" + (c.html ? c.html(r) : esc(c.val ? c.val(r) : "")) + "</td>";
        }).join("") + "</tr>";
      }).join("");
      count.textContent = data.length + " of " + rows.length + " rows";
    }
    function c0() { return false; }
    draw();
    return { redraw: draw };
  }

  window.PK = {
    SRC: SRC, NAV: NAV, esc: esc, money: money, fmtDate: fmtDate, fmtTime: fmtTime,
    load: load, loadSources: loadSources, srcLink: srcLink, srcLinks: srcLinks,
    flagTags: flagTags, entryBadge: entryBadge, unv: unv, renderNav: renderNav, table: table
  };
})();
