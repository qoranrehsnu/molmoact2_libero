#!/usr/bin/env python3
import html
import json
import sys
from pathlib import Path


def color(pct: float) -> str:
    if pct >= 98:
        return "#1f9d55"
    if pct >= 95:
        return "#7aa61f"
    if pct >= 90:
        return "#c28a16"
    return "#c2410c"


def suite_bar(name: str, pct: float, n_episodes: int) -> str:
    return f"""
      <div class="row">
        <div class="label">{html.escape(name)}</div>
        <div class="barwrap"><div class="bar" style="width:{pct:.1f}%;background:{color(pct)}"></div></div>
        <div class="value">{pct:.1f}% <span>{n_episodes} eps</span></div>
      </div>"""


def task_card(group: str, task_id: int, pct: float, n_success: int, n_total: int) -> str:
    short_group = html.escape(str(group)).replace("libero_", "")
    return f"""
      <div class="task" title="{html.escape(str(group))} task {task_id}: {n_success}/{n_total}">
        <div class="tasktop"><span>{short_group}</span><b>{task_id}</b></div>
        <div class="mini"><div style="width:{pct:.1f}%;background:{color(pct)}"></div></div>
        <div class="taskpct">{pct:.1f}%</div>
        <div class="taskn">{n_success}/{n_total}</div>
      </div>"""


def main() -> int:
    src = Path(sys.argv[1])
    out = Path(sys.argv[2])
    data = json.loads(src.read_text())

    suite_rows = []
    for name, metrics in data.get("per_group", {}).items():
        suite_rows.append((name, float(metrics.get("pc_success", 0)), int(metrics.get("n_episodes", 0))))

    task_rows = []
    for item in data.get("per_task", []):
        group = str(item.get("task_group"))
        task_id = int(item.get("task_id"))
        successes = item.get("metrics", {}).get("successes", [])
        n_success = sum(bool(x) for x in successes)
        n_total = len(successes) or 1
        pct = 100 * n_success / n_total
        task_rows.append((group, task_id, pct, n_success, n_total))

    failed = [row for row in task_rows if row[3] != row[4]]
    failed.sort(key=lambda row: row[2])

    overall = data.get("overall", {})
    failed_rows = "\n".join(
        "<tr><td>{}</td><td>{}</td><td>{}/{}</td><td>{:.1f}%</td></tr>".format(
            html.escape(group), task_id, n_success, n_total, pct
        )
        for group, task_id, pct, n_success, n_total in failed
    )

    doc = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>MolmoAct2 LIBERO Eval Success</title>
<style>
  body {{ margin: 0; font-family: system-ui, -apple-system, Segoe UI, sans-serif; background: #f6f7f9; color: #17202a; }}
  main {{ max-width: 1180px; margin: 0 auto; padding: 28px; }}
  h1 {{ font-size: 28px; margin: 0 0 8px; }}
  h2 {{ font-size: 18px; margin: 28px 0 14px; }}
  .meta {{ color: #586574; font-size: 14px; margin-bottom: 20px; }}
  .summary {{ display: grid; grid-template-columns: repeat(4, minmax(160px, 1fr)); gap: 12px; }}
  .stat, .panel {{ background: white; border: 1px solid #dde2e7; border-radius: 8px; padding: 16px; }}
  .stat .k {{ color: #657181; font-size: 13px; }}
  .stat .v {{ font-size: 28px; font-weight: 700; margin-top: 6px; }}
  .row {{ display: grid; grid-template-columns: 130px 1fr 120px; gap: 12px; align-items: center; margin: 12px 0; }}
  .label {{ font-weight: 650; }}
  .barwrap {{ height: 22px; background: #e8edf2; border-radius: 5px; overflow: hidden; }}
  .bar {{ height: 100%; }}
  .value {{ text-align: right; font-weight: 700; }}
  .value span {{ display: block; color: #6b7684; font-size: 12px; font-weight: 500; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(112px, 1fr)); gap: 10px; }}
  .task {{ background: white; border: 1px solid #dde2e7; border-radius: 8px; padding: 10px; }}
  .tasktop {{ display: flex; justify-content: space-between; color: #52606f; font-size: 12px; }}
  .mini {{ height: 8px; background: #e8edf2; border-radius: 99px; overflow: hidden; margin: 10px 0 8px; }}
  .mini div {{ height: 100%; }}
  .taskpct {{ font-size: 20px; font-weight: 750; }}
  .taskn {{ color: #6b7684; font-size: 12px; margin-top: 2px; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid #dde2e7; border-radius: 8px; overflow: hidden; }}
  th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #e7ebef; }}
  th {{ background: #eef2f6; font-size: 13px; }}
  tr:last-child td {{ border-bottom: 0; }}
  @media (max-width: 760px) {{ main {{ padding: 16px; }} .summary {{ grid-template-columns: 1fr 1fr; }} .row {{ grid-template-columns: 1fr; }} .value {{ text-align: left; }} }}
</style>
</head>
<body>
<main>
  <h1>MolmoAct2 LIBERO Full Eval</h1>
  <div class="meta">Source: {html.escape(str(src))}</div>
  <section class="summary">
    <div class="stat"><div class="k">Overall Success</div><div class="v">{float(overall.get("pc_success", 0)):.1f}%</div></div>
    <div class="stat"><div class="k">Episodes</div><div class="v">{int(overall.get("n_episodes", 0))}</div></div>
    <div class="stat"><div class="k">Eval Hours</div><div class="v">{float(overall.get("eval_s", 0)) / 3600:.2f}</div></div>
    <div class="stat"><div class="k">Seconds / Episode</div><div class="v">{float(overall.get("eval_ep_s", 0)):.2f}</div></div>
  </section>

  <h2>Suite Success Rate</h2>
  <section class="panel">
    {"".join(suite_bar(*row) for row in suite_rows)}
  </section>

  <h2>Task Success Rate</h2>
  <section class="grid">
    {"".join(task_card(*row) for row in task_rows)}
  </section>

  <h2>Failed Tasks, Lowest First</h2>
  <table>
    <thead><tr><th>Suite</th><th>Task</th><th>Success</th><th>Rate</th></tr></thead>
    <tbody>
      {failed_rows}
    </tbody>
  </table>
</main>
</body>
</html>
"""
    out.write_text(doc)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
