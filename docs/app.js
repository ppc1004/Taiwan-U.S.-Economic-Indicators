// Taiwan & U.S. Economic Indicators - plain JavaScript, no libraries.

const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const LIGHT = {
  "blue":        { label: "Blue",        meaning: "Slump",        c: "--blue" },
  "yellow-blue": { label: "Yellow-blue", meaning: "Cooling down", c: "--yblue" },
  "green":       { label: "Green",       meaning: "Stable",       c: "--green" },
  "yellow-red":  { label: "Yellow-red",  meaning: "Warming up",   c: "--yred" },
  "red":         { label: "Red",         meaning: "Overheating",  c: "--red" },
};
const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const fmtMonth = (d) => `${MONTHS[+d.slice(5, 7) - 1]} ${d.slice(0, 4)}`;
const NS = "http://www.w3.org/2000/svg";
const tip = document.getElementById("tip");

function el(tag, attrs = {}, parent) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}

function showTip(html, ev) {
  tip.innerHTML = html;
  tip.style.opacity = 1;
  const w = tip.offsetWidth, h = tip.offsetHeight;
  let x = ev.clientX + 14, y = ev.clientY - h - 10;
  if (x + w > window.innerWidth - 8) x = ev.clientX - w - 14;
  if (y < 8) y = ev.clientY + 16;
  tip.style.left = x + "px"; tip.style.top = y + "px";
}
const hideTip = () => (tip.style.opacity = 0);

/* A line chart with one y-axis, a crosshair and a tooltip.
   o = { n, height, yMin, yMax, yTicks, yFmt, xTick(i) -> label|null,
         series: [{ name, color, values, width, opacity, markers, label }],
         bands: [{ y0, y1, color, opacity }], shade: [[i0, i1]],
         strip: [colors], tip(i) -> html } */
function lineChart(box, o) {
  const draw = () => {
    box.innerHTML = "";
    const named = o.series.filter((s) => s.label);
    if (named.length > 1) {
      const lg = document.createElement("div");
      lg.className = "chart-legend";
      lg.innerHTML = named.map((s) => `<span><i style="background:${s.color}"></i>${s.name}</span>`).join("");
      box.appendChild(lg);
    }
    const W = Math.max(box.clientWidth, 300), small = W < 560;
    const H = o.height || (small ? 240 : 300);
    const stripH = o.strip ? 14 : 0;
    const m = { l: 44, r: named.length && !small ? 64 : 14, t: 10, b: 26 + stripH + (stripH ? 6 : 0) };
    const iw = W - m.l - m.r, ih = H - m.t - m.b;
    const x = (i) => m.l + (o.n === 1 ? 0 : (i / (o.n - 1)) * iw);
    const y = (v) => m.t + (1 - (v - o.yMin) / (o.yMax - o.yMin)) * ih;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img" }, box);

    (o.bands || []).forEach((b) => el("rect", { x: m.l, width: iw, y: y(b.y1), height: y(b.y0) - y(b.y1), fill: b.color, opacity: b.opacity ?? 0.12 }, svg));
    const step = o.n > 1 ? iw / (o.n - 1) : iw;
    (o.shade || []).forEach(([a, b]) => el("rect", { x: x(a) - step / 2, width: x(b) - x(a) + step, y: m.t, height: ih, fill: css("--rec") }, svg));

    o.yTicks.forEach((t) => {
      el("line", { x1: m.l, x2: m.l + iw, y1: y(t), y2: y(t), class: "grid" }, svg);
      el("text", { x: m.l - 8, y: y(t) + 4, "text-anchor": "end" }, svg).textContent = o.yFmt ? o.yFmt(t) : t;
    });
    for (let i = 0; i < o.n; i++) {
      const lab = o.xTick(i, small);
      if (lab) el("text", { x: x(i), y: H - 8, "text-anchor": "middle" }, svg).textContent = lab;
    }
    if (o.strip) o.strip.forEach((c, i) => el("rect", { x: x(i) - step / 2, width: step + 0.5, y: m.t + ih + 6, height: stripH, fill: c }, svg));

    o.series.forEach((s) => {
      let d = "";
      s.values.forEach((v, i) => { if (v == null) return; d += (d && s.values[i - 1] != null ? "L" : "M") + x(i).toFixed(1) + "," + y(v).toFixed(1); });
      el("path", { d, fill: "none", stroke: s.color, "stroke-width": s.width || 2, opacity: s.opacity ?? 1, "stroke-linejoin": "round", "stroke-linecap": "round" }, svg);
      if (s.markers) s.values.forEach((v, i) => v != null && el("circle", { cx: x(i), cy: y(v), r: 3, fill: s.color, stroke: css("--card"), "stroke-width": 1.5 }, svg));
      if (s.label && !small) {
        const last = s.values.length - 1;
        el("text", { x: x(last) + 8, y: y(s.values[last]) + 4, class: "lbl", fill: s.color, style: `fill:${s.color}` }, svg).textContent = s.short || s.name;
      }
    });

    const hair = el("line", { y1: m.t, y2: m.t + ih, class: "hair", opacity: 0 }, svg);
    const dots = o.series.filter((s) => s.hover !== false).map((s) => el("circle", { r: 4.5, fill: s.color, stroke: css("--card"), "stroke-width": 2, opacity: 0 }, svg));
    const hit = el("rect", { x: m.l - step / 2, y: 0, width: iw + step, height: H, fill: "transparent" }, svg);
    const move = (ev) => {
      const r = svg.getBoundingClientRect();
      const px = ((ev.clientX - r.left) / r.width) * W;
      const i = Math.max(0, Math.min(o.n - 1, Math.round(((px - m.l) / iw) * (o.n - 1))));
      hair.setAttribute("x1", x(i)); hair.setAttribute("x2", x(i)); hair.setAttribute("opacity", 1);
      o.series.filter((s) => s.hover !== false).forEach((s, k) => {
        const v = s.values[i];
        dots[k].setAttribute("opacity", v == null ? 0 : 1);
        if (v != null) { dots[k].setAttribute("cx", x(i)); dots[k].setAttribute("cy", y(v)); }
      });
      showTip(o.tip(i), ev);
    };
    hit.addEventListener("pointermove", move);
    hit.addEventListener("pointerdown", move);
    hit.addEventListener("pointerleave", () => { hair.setAttribute("opacity", 0); dots.forEach((d) => d.setAttribute("opacity", 0)); hideTip(); });
  };
  draw();
  let t;
  new ResizeObserver(() => { clearTimeout(t); t = setTimeout(draw, 120); }).observe(box);
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", draw);
}

const tipRow = (color, name, val) => `<div class="row"><span><i class="sw" style="background:${color}"></i>${name}</span><span>${val}</span></div>`;

/* ---------- 1. U.S. light ---------- */
function renderLight(d) {
  const L = d.latest, info = LIGHT[L.light];
  document.getElementById("now").innerHTML = `
    <div class="bulb" style="color:${css(info.c)}"></div>
    <div>
      <p class="big">${info.label}: ${info.meaning}</p>
      <p class="meta">${fmtMonth(L.date)} · score ${L.score} out of 45${L.recession ? " · in an official recession" : ""}</p>
    </div>`;
  document.getElementById("legend-lights").innerHTML = d.method.lights.slice().reverse().map((l, k, arr) => {
    const hi = k === arr.length - 1 ? 45 : arr[k + 1].min - 1;
    return `<span><i style="background:${css(LIGHT[l.light].c)}"></i>${l.label} (${l.min}–${hi}): ${l.meaning}</span>`;
  }).join("");

  const M = d.months;
  const shade = [];
  M.forEach((m, i) => { if (m.recession) { if (shade.length && shade.at(-1)[1] === i - 1) shade.at(-1)[1] = i; else shade.push([i, i]); } });
  const bands = d.method.lights.map((l, k, arr) => ({ y0: l.min - 0.5, y1: k === 0 ? 45 : arr[k - 1].min - 0.5, color: css(LIGHT[l.light].c), opacity: 0.14 }));
  lineChart(document.getElementById("chart-light"), {
    n: M.length, yMin: 9, yMax: 45, yTicks: [9, 16, 22, 31, 37, 45],
    xTick: (i, small) => { const y = +M[i].date.slice(0, 4); return M[i].date.endsWith("-01") && y % (small ? 8 : 4) === 0 ? y : null; },
    bands, shade,
    strip: M.map((m) => css(LIGHT[m.light].c)),
    series: [{ name: "Score", color: css("--ink"), values: M.map((m) => m.score), width: 1.8 }],
    tip: (i) => { const m = M[i], li = LIGHT[m.light];
      return `<b>${fmtMonth(m.date)}</b>${tipRow(css(li.c), li.label, m.score + " / 45")}${m.recession ? '<div class="small" style="margin:2px 0 0">Official recession</div>' : ""}`; },
  });

  const pts = (p, color) => `<span class="dots" aria-label="${p} of 5 points">${[1,2,3,4,5].map((k) => `<i style="${k <= p ? `background:${color}` : ""}"></i>`).join("")}</span>`;
  const pointColor = { 1: "--blue", 2: "--yblue", 3: "--green", 4: "--yred", 5: "--red" };
  document.getElementById("ind-table").innerHTML = `
    <thead><tr><th>Indicator</th><th class="n">Latest</th><th>Points</th><th class="hide-sm">Replaces Taiwan's</th></tr></thead>
    <tbody>${d.indicators.map((ind) => {
      const v = L.indicators[ind.key];
      const val = ind.transform === "yoy" ? `${v.value > 0 ? "+" : ""}${v.value.toFixed(1)}% <span class="tw hide-sm">vs. a year ago</span>` : `${v.value.toFixed(1)} <span class="tw">index</span>`;
      return `<tr><td>${ind.name}</td><td class="n">${val}</td><td>${pts(v.points, css(pointColor[v.points]))}</td><td class="tw hide-sm">${ind.taiwan}</td></tr>`;
    }).join("")}</tbody>`;
  document.getElementById("updated").textContent = `U.S. data last updated ${d.updated}.`;
}

/* ---------- 2. Trade ---------- */
function renderTrade(d) {
  const US = css("--us"), CN = css("--cn");
  const M = d.monthly, A = d.annual;
  const B = (v) => "$" + v.toFixed(1) + "B";

  lineChart(document.getElementById("chart-exports"), {
    n: M.length, yMin: 0, yMax: 12, yTicks: [0, 3, 6, 9, 12], yFmt: (t) => "$" + t + "B",
    xTick: (i, small) => { const y = +M[i].date.slice(0, 4); return M[i].date.endsWith("-01") && y % (small ? 8 : 4) === 0 ? y : null; },
    series: [
      { name: "U.S. monthly", color: US, values: M.map((m) => m.us_exp), width: 1, opacity: 0.35, hover: false },
      { name: "Mainland China monthly", color: CN, values: M.map((m) => m.cn_exp), width: 1, opacity: 0.35, hover: false },
      { name: "U.S.", color: US, values: d.trend.us_exp, width: 2.5, short: "U.S.", label: true },
      { name: "Mainland China", short: "China", color: CN, values: d.trend.cn_exp, width: 2.5, label: true },
    ],
    tip: (i) => `<b>${fmtMonth(M[i].date)}</b>Exports to:${tipRow(US, "U.S.", B(M[i].us_exp))}${tipRow(CN, "Mainland China", B(M[i].cn_exp))}`,
  });

  const yearTick = (i, small) => (A[i].year % (small ? 5 : 2) === 0 ? A[i].year : null);
  lineChart(document.getElementById("chart-share"), {
    n: A.length, yMin: 0, yMax: 35, yTicks: [0, 10, 20, 30], yFmt: (t) => t + "%", xTick: yearTick,
    series: [
      { name: "U.S.", color: US, values: A.map((a) => a.us_share), markers: true, label: true },
      { name: "Mainland China", color: CN, values: A.map((a) => a.cn_share), markers: true, label: true, short: "China" },
    ],
    tip: (i) => `<b>${A[i].year}</b>Share of Taiwan's exports:${tipRow(US, "U.S.", A[i].us_share.toFixed(1) + "%")}${tipRow(CN, "Mainland China", A[i].cn_share.toFixed(1) + "%")}`,
  });

  lineChart(document.getElementById("chart-surplus"), {
    n: A.length, yMin: 0, yMax: 70, yTicks: [0, 20, 40, 60], yFmt: (t) => "$" + t + "B", xTick: yearTick,
    series: [
      { name: "With the U.S.", color: US, values: A.map((a) => a.us_surplus), markers: true, label: true, short: "U.S." },
      { name: "With mainland China", color: CN, values: A.map((a) => a.cn_surplus), markers: true, label: true, short: "China" },
    ],
    tip: (i) => `<b>${A[i].year}</b>Trade surplus:${tipRow(US, "With the U.S.", B(A[i].us_surplus))}${tipRow(CN, "With mainland China", B(A[i].cn_surplus))}`,
  });
}

fetch("data/us_light.json").then((r) => r.json()).then(renderLight).catch((e) => console.error("U.S. light:", e));
fetch("data/taiwan_trade.json").then((r) => r.json()).then(renderTrade).catch((e) => console.error("Trade:", e));

/* ---------- 3. Products ---------- */
function renderProducts(d) {
  const US = css("--us"), CN = css("--cn");
  const ue = d.data.us_exports, ce = d.data.cn_exports, Y = ue.years;
  const M = "Machinery and electrical equipment", O = "Optical and precision instruments";
  const B = (v) => "$" + v.toFixed(1) + "B";
  const yearTick = (i, small) => (Y[i] % (small ? 5 : 2) === 0 ? Y[i] : null);

  lineChart(document.getElementById("chart-mach"), {
    n: Y.length, yMin: 0, yMax: 100, yTicks: [0, 25, 50, 75, 100], yFmt: (t) => "$" + t + "B", xTick: yearTick,
    series: [
      { name: "To the U.S.", short: "U.S.", color: US, values: ue[M], markers: true, label: true },
      { name: "To mainland China", short: "China", color: CN, values: ce[M], markers: true, label: true },
    ],
    tip: (i) => `<b>${Y[i]}</b>Machinery exports:${tipRow(US, "To the U.S.", B(ue[M][i]))}${tipRow(CN, "To mainland China", B(ce[M][i]))}`,
  });

  const shU = ue[M].map((v, i) => (v / ue.total[i]) * 100), shC = ce[M].map((v, i) => (v / ce.total[i]) * 100);
  lineChart(document.getElementById("chart-mach-share"), {
    n: Y.length, yMin: 0, yMax: 100, yTicks: [0, 25, 50, 75, 100], yFmt: (t) => t + "%", xTick: yearTick,
    series: [
      { name: "Exports to the U.S.", short: "U.S.", color: US, values: shU, markers: true, label: true },
      { name: "Exports to mainland China", short: "China", color: CN, values: shC, markers: true, label: true },
    ],
    tip: (i) => `<b>${Y[i]}</b>Machinery share of exports:${tipRow(US, "To the U.S.", shU[i].toFixed(0) + "%")}${tipRow(CN, "To mainland China", shC[i].toFixed(0) + "%")}`,
  });

  lineChart(document.getElementById("chart-optical"), {
    n: Y.length, yMin: 0, yMax: 20, yTicks: [0, 5, 10, 15, 20], yFmt: (t) => "$" + t + "B", xTick: yearTick,
    series: [{ name: "To mainland China", color: CN, values: ce[O], markers: true }],
    tip: (i) => `<b>${Y[i]}</b>Optical and precision instruments:${tipRow(CN, "To mainland China", B(ce[O][i]))}`,
  });
}
fetch("data/taiwan_products.json").then((r) => r.json()).then(renderProducts).catch((e) => console.error("Products:", e));

/* ---------- 4. Export orders ---------- */
function renderOrders(d) {
  const Y = d.years, m = d.markets, B = (v) => "$" + v.toFixed(1) + "B";
  const yearTick = (i, small) => (Y[i] % (small ? 5 : 3) === 0 ? Y[i] : null);
  const S = [
    { k: "us", name: "U.S.", color: css("--us") },
    { k: "china_hk", name: "China and Hong Kong", short: "China+HK", color: css("--cn") },
    { k: "asean", name: "Southeast Asia", short: "SE Asia", color: css("--c3") },
    { k: "europe", name: "Europe", color: css("--c4") },
    { k: "japan", name: "Japan", color: css("--c5") },
  ];
  lineChart(document.getElementById("chart-orders"), {
    n: Y.length, yMin: 0, yMax: 250, yTicks: [0, 50, 100, 150, 200, 250], yFmt: (t) => "$" + t + "B", xTick: yearTick,
    series: S.map((s) => ({ name: s.name, short: s.short, color: s.color, values: m[s.k], label: true })),
    tip: (i) => `<b>${Y[i]}</b>Orders from:${S.map((s) => tipRow(s.color, s.name, B(m[s.k][i]))).join("")}<div class="row"><span>All buyers</span><span>${B(d.total[i])}</span></div>`,
  });
  const two = [S[2], S[3]];
  lineChart(document.getElementById("chart-asean"), {
    n: Y.length, yMin: 0, yMax: 150, yTicks: [0, 50, 100, 150], yFmt: (t) => "$" + t + "B", xTick: yearTick,
    series: two.map((s) => ({ name: s.name, short: s.short, color: s.color, values: m[s.k], markers: true, label: true })),
    tip: (i) => `<b>${Y[i]}</b>Orders from:${two.map((s) => tipRow(s.color, s.name, B(m[s.k][i]))).join("")}`,
  });
}

/* ---------- 5. Investment ---------- */
function renderInvestment(d) {
  const Y = d.years, US = css("--us"), CN = css("--cn"), OT = css("--c3");
  const B = (v) => (v == null ? "n/a" : "$" + v.toFixed(1) + "B");
  const yearTick = (i, small) => (Y[i] % (small ? 5 : 3) === 0 ? Y[i] : null);
  lineChart(document.getElementById("chart-inv"), {
    n: Y.length, yMin: 0, yMax: 50, yTicks: [0, 10, 20, 30, 40, 50], yFmt: (t) => "$" + t + "B", xTick: yearTick,
    series: [
      { name: "All other countries", short: "Others", color: OT, values: d.other_countries, markers: true, label: true },
      { name: "Mainland China", short: "China", color: CN, values: d.china, markers: true, label: true },
    ],
    tip: (i) => `<b>${Y[i]}</b>Approved investment:${tipRow(OT, "All other countries", B(d.other_countries[i]))}${tipRow(CN, "Mainland China", B(d.china[i]))}<div class="row"><span>China's share</span><span>${d.china_share[i]}%</span></div>`,
  });
  const k0 = Y.indexOf(2016), Ys = Y.slice(k0), us = d.us.slice(k0), cn = d.china.slice(k0);
  lineChart(document.getElementById("chart-inv-us"), {
    n: Ys.length, yMin: 0, yMax: 15, yTicks: [0, 5, 10, 15], yFmt: (t) => "$" + t + "B", xTick: (i) => Ys[i],
    series: [
      { name: "U.S.", color: US, values: us, markers: true, label: true },
      { name: "Mainland China", short: "China", color: CN, values: cn, markers: true, label: true },
    ],
    tip: (i) => `<b>${Ys[i]}</b>Approved investment:${tipRow(US, "U.S.", B(us[i]))}${tipRow(CN, "Mainland China", B(cn[i]))}`,
  });
  lineChart(document.getElementById("chart-inv-cn"), {
    n: Y.length, yMin: 0, yMax: 4000, yTicks: [0, 1000, 2000, 3000, 4000], yFmt: (t) => t.toLocaleString(), xTick: yearTick,
    series: [{ name: "Projects in mainland China", color: CN, values: d.china_projects, markers: true }],
    tip: (i) => `<b>${Y[i]}</b>Mainland China:${tipRow(CN, "Approved projects", d.china_projects[i].toLocaleString())}${tipRow(CN, "Approved amount", B(d.china[i]))}`,
  });
}
fetch("data/taiwan_orders.json").then((r) => r.json()).then(renderOrders).catch((e) => console.error("Orders:", e));
fetch("data/taiwan_investment.json").then((r) => r.json()).then(renderInvestment).catch((e) => console.error("Investment:", e));
