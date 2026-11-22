/* Standalone browser view for the computed project report. */
window.drawProjectView = function (host, report, input) {
  "use strict";
  function el(tag, text, css) {
    const item = document.createElement(tag);
    if (text != null) item.textContent = String(text);
    if (css) item.style.cssText = css;
    return item;
  }
  const figure = el("figure", null, "box-sizing:border-box;margin:12px 0 16px;padding:12px 14px;border-radius:9px;background:#172329;color:#f4f5f2;max-height:210px;overflow:auto;font:13px/1.35 system-ui,sans-serif;text-align:left");
  const head = el("figcaption", "Continuous footage against the shot list", "font-size:15px;font-weight:700;letter-spacing:-.015em;color:#f3c787;margin-bottom:7px");
  figure.append(head);
  host.replaceChildren(figure);
  const rows = Array.isArray(report && report.rows) ? report.rows : [];
  if (!rows.length) {
    figure.append(el("p", "No findings to display.", "margin:0"));
    return;
  }

  const byShot = new Map((input.shot_list || []).map(shot => [shot.shot.trim(), shot.seconds]));
  const shown = rows.slice(0, 4);
  const grid = el("div", null, "display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,210px),1fr));gap:8px");
  for (const row of shown) {
    const planned = byShot.get(row["Planned shot"]);
    const available = Number(row["Usable seconds"]);
    const status = row.Status;
    const tint = status === "Covered" ? "#80d3bc" : status === "Missing" ? "#ffad96" : "#f3c787";
    const cell = el("div", null, "min-width:0;background:#26363c;padding:7px 10px;border-radius:5px");
    const title = el("div", row["Planned shot"], "white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:650");
    title.title = row["Planned shot"];
    const rail = el("div", null, "height:5px;margin:5px 0;background:#4a585b;border-radius:4px;overflow:hidden");
    const percent = planned > 0 ? Math.min(100, Math.max(0, available / planned * 100)) : 0;
    rail.append(el("div", null, "height:100%;background:" + tint + ";width:" + percent + "%"));
    cell.append(title, rail, el("div", status + " · " + available + " / " + planned + " s", "font:11px/1.3 system-ui;color:#e2e9e6"));
    grid.append(cell);
  }
  figure.append(grid);
  if (rows.length > shown.length) figure.append(el("small", "Showing the first four planned shots."));

};
