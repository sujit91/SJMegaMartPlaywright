"""Per-test HTML reports plus a non-overwriting management summary."""

from __future__ import annotations

import base64
import html
import re
import shutil
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pytest

from config.settings import BASE_URL, HEADLESS
from utils.steps import add_step, get_steps, install_action_hooks, reset_steps, take_screenshot

REPORT_DIR = Path("reports")
MODULE_TITLES = {
    "test_01_login": "Login",
    "test_02_signup": "Sign Up",
    "test_03_home": "Home / Navigation",
    "test_04_search": "Search",
    "test_05_catalog": "Catalog",
    "test_06_cart": "Cart",
    "test_07_checkout": "Checkout",
    "test_08_payment": "Payment",
}

_records: dict[str, dict] = {}
_started = 0.0
_run_id = ""
_run_dir = REPORT_DIR / "runs" / "pending"

REPORT_CSS = """
:root { --navy:#0f2744; --ok:#047857; --warn:#b45309; --bad:#b91c1c; --bg:#f4f7fb; --card:#fff; --line:#e5e7eb; --muted:#6b7280; }
* { box-sizing: border-box; }
body { margin:0; font-family:"Segoe UI",Calibri,Arial,sans-serif; background:var(--bg); color:#111827; }
header { background:linear-gradient(120deg,#0f2744 0%,#134e4a 100%); color:#fff; padding:28px 36px 24px; }
header .kicker { letter-spacing:.14em; font-size:12px; opacity:.8; text-transform:uppercase; }
header h1 { margin:6px 0 8px; font-size:28px; font-weight:650; }
header p { margin:0; opacity:.9; }
main { padding:24px 36px 48px; max-width:1100px; margin:0 auto; }
.kpis { display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:12px; margin:8px 0 20px; }
.kpi { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px 18px; }
.kpi .label { color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.06em; }
.kpi .value { font-size:28px; font-weight:700; margin-top:6px; }
.verdict { border-radius:12px; padding:16px 20px; margin-bottom:22px; font-weight:650; color:#fff; }
.verdict.go { background:var(--ok); }
.verdict.nogo { background:var(--bad); }
h2 { font-size:18px; margin:28px 0 10px; color:var(--navy); }
table { width:100%; border-collapse:collapse; background:var(--card); border-radius:12px; overflow:hidden; }
th, td { text-align:left; padding:10px 12px; border-bottom:1px solid var(--line); font-size:14px; }
th { background:#eef2f7; color:#374151; font-weight:650; }
.ok { color:var(--ok); font-weight:650; }
.warn { color:var(--warn); font-weight:650; }
.bad { color:var(--bad); font-weight:650; }
.pill { display:inline-block; padding:2px 10px; border-radius:999px; font-size:12px; color:#fff; }
.pill.ok { background:var(--ok); }
.pill.bad { background:var(--bad); }
.reason { font-family:Consolas,"Courier New",monospace; font-size:12px; color:#7f1d1d; }
.meta { color:var(--muted); font-size:13px; line-height:1.6; }
.empty { background:#ecfdf5; color:var(--ok); padding:14px 16px; border-radius:12px; }
ol.steps { margin:10px 0 0; padding-left:18px; }
ol.steps li { margin:6px 0; }
ol.steps li.failed { color:var(--bad); }
ol.steps img { display:block; max-width:100%; margin-top:8px; border:1px solid var(--line); border-radius:8px; }
video { width:100%; max-width:720px; margin-top:10px; border-radius:8px; background:#000; }
a { color:#0f766e; }
footer { color:var(--muted); font-size:12px; margin-top:28px; }
"""


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    global _run_id, _run_dir
    _run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    _run_dir = REPORT_DIR / "runs" / _run_id
    _run_dir.mkdir(parents=True, exist_ok=True)
    (_run_dir / "tests").mkdir(parents=True, exist_ok=True)
    (_run_dir / "artifacts").mkdir(parents=True, exist_ok=True)
    _apply_optional_plugin_defaults(config)
    try:
        install_action_hooks()
    except Exception:
        pass
    try:
        from pytest_metadata.plugin import metadata_key

        meta = config.stash[metadata_key]
        meta["Project"] = "SJ MegaMart"
        meta["Application"] = BASE_URL
        meta["Browser"] = "Chromium"
        meta["Mode"] = "Headless" if HEADLESS else "Headed"
        meta["Run"] = _run_id
    except Exception:
        pass


def _apply_optional_plugin_defaults(config):
    option = getattr(config, "option", None)
    if option is None:
        return
    if hasattr(option, "htmlpath") and not option.htmlpath:
        option.htmlpath = str(_run_dir / "pytest-report.html")
    if hasattr(option, "self_contained_html"):
        option.self_contained_html = True
    if getattr(option, "screenshot", None) == "off":
        option.screenshot = "only-on-failure"
    if hasattr(option, "full_page_screenshot"):
        option.full_page_screenshot = True
    if getattr(option, "video", None) == "off":
        option.video = "retain-on-failure"
    if getattr(option, "output", None) in (None, "test-results"):
        option.output = str(_run_dir / "artifacts")


@pytest.hookimpl(optionalhook=True)
def pytest_html_report_title(report):
    report.title = "SJ MegaMart – Playwright Detailed Report"


def pytest_sessionstart(session):
    global _started
    _started = time.time()
    _records.clear()


def pytest_runtest_setup(item):
    reset_steps()


def pytest_runtest_logreport(report):
    rec = _records.setdefault(
        report.nodeid,
        {
            "nodeid": report.nodeid,
            "outcome": "passed",
            "duration": 0.0,
            "longrepr": "",
            "steps": [],
            "video": "",
            "report_href": "",
        },
    )
    rec["duration"] += report.duration or 0.0
    if report.when == "call":
        rec["outcome"] = report.outcome
        rec["steps"] = get_steps()
        if report.failed:
            rec["longrepr"] = _short_error(report)
    elif report.failed and report.when == "setup":
        rec["outcome"] = "error"
        rec["longrepr"] = _short_error(report)
    elif report.skipped and report.when != "teardown" and rec["outcome"] == "passed":
        rec["outcome"] = "skipped"
        rec["longrepr"] = _short_error(report)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    extras = getattr(rep, "extras", [])
    if rep.when == "call":
        if rep.failed:
            page = item.funcargs.get("page") or item.funcargs.get("logged_in_page")
            steps = get_steps()
            if page is not None and not any(step["status"] == "failed" for step in steps):
                shot = take_screenshot(page, "assertion-failed")
                add_step("Assertion failed", "failed", screenshot=shot, error=_short_error(rep))
                steps = get_steps()
            rec = _records.get(rep.nodeid)
            if rec is not None:
                rec["steps"] = steps
                rec["longrepr"] = rec.get("longrepr") or _short_error(rep)
        extras.extend(_html_step_extras(get_steps()))
        rep.extras = extras
        item._sj_call_report = rep
    elif rep.when == "teardown":
        rec = _records.get(item.nodeid)
        video = _find_video(item.nodeid)
        call_report = getattr(item, "_sj_call_report", None)
        if rec is not None and video:
            rec["video"] = video.replace("\\", "/")
            if call_report is not None:
                try:
                    from pytest_html import extras as html_extras

                    payload = base64.b64encode(Path(video).read_bytes()).decode("ascii")
                    extras = getattr(call_report, "extras", [])
                    extras.append(
                        html_extras.video(
                            payload,
                            name="Test video",
                            mime_type="video/webm",
                            extension="webm",
                        )
                    )
                    call_report.extras = extras
                except Exception:
                    pass
        if rec is not None:
            rec["steps"] = rec.get("steps") or get_steps()
            write_test_report(rec)


def pytest_sessionfinish(session, exitstatus):
    write_management_report(list(_records.values()), time.time() - _started, exitstatus)
    _write_runs_index()


def _test_folder(nodeid: str) -> Path:
    file_part = Path(nodeid.split("::")[0]).stem or "other"
    name = re.sub(r"[^\w.-]+", "_", nodeid.split("::")[-1]).strip("_") or "test"
    return _run_dir / "tests" / file_part / name


def write_test_report(rec: dict) -> Path:
    folder = _test_folder(rec["nodeid"])
    folder.mkdir(parents=True, exist_ok=True)
    video_name = ""
    src = rec.get("video") or ""
    if src and Path(src).exists():
        shutil.copy2(src, folder / "video.webm")
        video_name = "video.webm"
    href = folder.relative_to(_run_dir).joinpath("report.html").as_posix()
    rec["report_href"] = href
    (folder / "report.html").write_text(_render_test(rec, video_name), encoding="utf-8")
    return folder / "report.html"


def write_management_report(records: list[dict], duration: float, exitstatus: int) -> Path:
    _run_dir.mkdir(parents=True, exist_ok=True)
    counts = Counter(r["outcome"] for r in records)
    total = len(records)
    passed = counts.get("passed", 0)
    failed = counts.get("failed", 0) + counts.get("error", 0)
    skipped = counts.get("skipped", 0)
    pass_rate = (passed / total * 100) if total else 0.0
    go = failed == 0 and total > 0
    generated = datetime.now(timezone.utc).astimezone().strftime("%d %b %Y, %I:%M %p")
    by_module: dict[str, Counter] = defaultdict(Counter)
    for rec in records:
        by_module[_module_of(rec["nodeid"])][rec["outcome"]] += 1
        if not rec.get("report_href"):
            write_test_report(rec)
    html_doc = _render_summary(
        generated=generated,
        duration=duration,
        total=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        pass_rate=pass_rate,
        go=go,
        by_module=by_module,
        failures=[r for r in records if r["outcome"] in ("failed", "error")],
        records=records,
    )
    summary = _run_dir / "management-report.html"
    summary.write_text(html_doc, encoding="utf-8")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(summary, REPORT_DIR / "management-report.html")
    pytest_html = _run_dir / "pytest-report.html"
    if pytest_html.exists():
        shutil.copy2(pytest_html, REPORT_DIR / "report.html")
    latest = REPORT_DIR / "latest"
    if latest.exists() or latest.is_symlink():
        try:
            if latest.is_dir() and not latest.is_symlink():
                shutil.rmtree(latest, ignore_errors=True)
            else:
                latest.unlink()
        except OSError:
            pass
    try:
        latest.symlink_to(_run_dir.resolve(), target_is_directory=True)
    except OSError:
        shutil.copytree(_run_dir, latest, dirs_exist_ok=True)
    return summary


def _write_runs_index() -> None:
    runs_root = REPORT_DIR / "runs"
    if not runs_root.exists():
        return
    rows = []
    for folder in sorted(runs_root.iterdir(), reverse=True):
        if not folder.is_dir():
            continue
        summary = folder / "management-report.html"
        if not summary.exists():
            continue
        rows.append(
            f"<tr><td><a href='runs/{_esc(folder.name)}/management-report.html'>{_esc(folder.name)}</a></td>"
            f"<td>{len(list((folder / 'tests').glob('**/report.html')))} test report(s)</td></tr>"
        )
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>SJ MegaMart report runs</title>
<style>{REPORT_CSS}</style></head><body>
<header><div class="kicker">History</div><h1>All execution runs</h1>
<p>Each run keeps its own folder so reports are never overwritten.</p></header>
<main><table><thead><tr><th>Run</th><th>Test reports</th></tr></thead>
<tbody>{''.join(rows) or '<tr><td colspan="2">No runs yet.</td></tr>'}</tbody></table>
<p class="meta">Latest summary: <a href="management-report.html">management-report.html</a></p>
</main></body></html>"""
    (REPORT_DIR / "index.html").write_text(page, encoding="utf-8")


def _html_step_extras(steps: list[dict]) -> list:
    extras = []
    try:
        from pytest_html import extras as html_extras
    except Exception:
        return extras
    if not steps:
        return extras
    rows = []
    for index, step in enumerate(steps, 1):
        mark = "FAIL" if step["status"] == "failed" else "PASS"
        rows.append(f"{index}. [{mark}] {html.escape(step['name'])}")
        if step.get("screenshot") and Path(step["screenshot"]).exists():
            extras.append(
                html_extras.image(
                    base64.b64encode(Path(step["screenshot"]).read_bytes()).decode("ascii"),
                    name=f"Failed step: {step['name'][:60]}",
                )
            )
    extras.insert(0, html_extras.html("<pre>" + "\n".join(rows) + "</pre>"))
    return extras


def _find_video(nodeid: str) -> str:
    try:
        from slugify import slugify
    except Exception:
        return ""
    folder = _run_dir / "artifacts" / slugify(nodeid)
    if folder.exists():
        videos = sorted(folder.glob("video*.webm"))
        if videos:
            return str(videos[0])
    artifacts = _run_dir / "artifacts"
    if artifacts.exists():
        videos = sorted(artifacts.rglob("video*.webm"))
        if videos:
            return str(videos[-1])
    return ""


def _img_data(path: str | None) -> str:
    if not path:
        return ""
    file = Path(path)
    if not file.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(file.read_bytes()).decode("ascii")


def _module_of(nodeid: str) -> str:
    match = re.search(r"(test_\d+_[a-z0-9_]+)", nodeid)
    key = match.group(1) if match else "other"
    return MODULE_TITLES.get(key, key.replace("_", " ").title())


def _short_error(report) -> str:
    text = str(report.longrepr) if report.longrepr else ""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for line in reversed(lines):
        if line.startswith("E ") or "AssertionError" in line or "Error:" in line:
            return line[2:].strip() if line.startswith("E ") else line
    return (lines[-1] if lines else "Failed")[:400]


def _esc(value) -> str:
    return html.escape(str(value))


def _render_test(rec: dict, video_name: str) -> str:
    title = rec["nodeid"].split("::")[-1]
    failed = rec["outcome"] in ("failed", "error")
    items = []
    for step in rec.get("steps") or []:
        shot = _img_data(step.get("screenshot")) if step["status"] == "failed" else ""
        img = f"<img alt='Failed step' src='{shot}'>" if shot else ""
        err = f"<div class='reason'>{_esc(step.get('error') or '')}</div>" if step.get("error") else ""
        items.append(
            f"<li class='{step['status']}'><span class='step-name'>{_esc(step['name'])}</span>{err}{img}</li>"
        )
    video_html = f"<h2>Video</h2><video controls src='{_esc(video_name)}'></video>" if video_name else ""
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{_esc(title)}</title>
<style>{REPORT_CSS}</style></head>
<body>
<header>
  <div class="kicker">Single test report · run {_esc(_run_id)}</div>
  <h1>{_esc(title)}</h1>
  <p>{_esc(_module_of(rec['nodeid']))} · {_esc(rec['nodeid'])}</p>
</header>
<main>
  <div class="verdict {'nogo' if failed else 'go'}">{rec['outcome'].upper()} · {rec['duration']:.1f}s</div>
  <p class="meta"><a href="../../../management-report.html">Back to run summary</a></p>
  {"<p class='reason'>" + _esc(rec.get("longrepr") or "") + "</p>" if failed else ""}
  <h2>Steps</h2>
  <ol class="steps">{''.join(items) or "<li>No UI steps captured.</li>"}</ol>
  {video_html}
  <footer>SJ MegaMart Playwright · this file is unique to this test and this run.</footer>
</main>
</body></html>"""


def _render_summary(**ctx) -> str:
    verdict = "GO – Ready for stakeholder demo / release" if ctx["go"] else "NO-GO – Failures need attention"
    verdict_class = "go" if ctx["go"] else "nogo"
    rate_class = "ok" if ctx["pass_rate"] >= 95 else "warn" if ctx["pass_rate"] >= 80 else "bad"
    module_rows = []
    for name in sorted(ctx["by_module"]):
        c = ctx["by_module"][name]
        mod_total = sum(c.values())
        mod_fail = c.get("failed", 0) + c.get("error", 0)
        module_rows.append(
            "<tr>"
            f"<td>{_esc(name)}</td><td>{mod_total}</td>"
            f"<td class='ok'>{c.get('passed', 0)}</td>"
            f"<td class='{'bad' if mod_fail else ''}'>{mod_fail}</td>"
            f"<td>{c.get('skipped', 0)}</td>"
            f"<td><span class='pill {('ok' if mod_fail == 0 else 'bad')}'>{'Pass' if mod_fail == 0 else 'Fail'}</span></td>"
            "</tr>"
        )
    test_rows = []
    for rec in ctx["records"]:
        failed = rec["outcome"] in ("failed", "error")
        href = rec.get("report_href") or "#"
        test_rows.append(
            "<tr>"
            f"<td><a href='{_esc(href)}'>{_esc(rec['nodeid'].split('::')[-1])}</a></td>"
            f"<td>{_esc(_module_of(rec['nodeid']))}</td>"
            f"<td><span class='pill {'bad' if failed else 'ok'}'>{rec['outcome'].upper()}</span></td>"
            f"<td>{rec['duration']:.1f}s</td>"
            f"<td class='reason'>{_esc(rec['longrepr'] if failed else '')}</td>"
            "</tr>"
        )
    fail_table = (
        "<div class='empty'>No failed cases in this run.</div>"
        if not ctx["failures"]
        else "<p class='meta'>Open a failed test link below for steps, screenshot and video.</p>"
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>SJ MegaMart – Run {_esc(_run_id)}</title>
<style>{REPORT_CSS}</style></head>
<body>
<header>
  <div class="kicker">Quality assurance · Executive summary · {_esc(_run_id)}</div>
  <h1>SJ MegaMart Automation Execution Report</h1>
  <p>Playwright · Python · Pytest &nbsp;|&nbsp; {_esc(ctx['generated'])} &nbsp;|&nbsp; Chromium ({'headless' if HEADLESS else 'headed'})</p>
</header>
<main>
  <div class="verdict {verdict_class}">{_esc(verdict)}</div>
  <div class="kpis">
    <div class="kpi"><div class="label">Total tests</div><div class="value">{ctx['total']}</div></div>
    <div class="kpi"><div class="label">Passed</div><div class="value ok">{ctx['passed']}</div></div>
    <div class="kpi"><div class="label">Failed</div><div class="value {'bad' if ctx['failed'] else 'ok'}">{ctx['failed']}</div></div>
    <div class="kpi"><div class="label">Skipped</div><div class="value">{ctx['skipped']}</div></div>
    <div class="kpi"><div class="label">Pass rate</div><div class="value {rate_class}">{ctx['pass_rate']:.1f}%</div></div>
    <div class="kpi"><div class="label">Duration</div><div class="value">{ctx['duration']:.0f}s</div></div>
  </div>
  <p class="meta">Application: {_esc(BASE_URL)}<br>This summary is for the whole run (Jenkins / group). Each test also has its own HTML report.</p>
  <h2>Results by business area</h2>
  <table><thead><tr><th>Area</th><th>Total</th><th>Passed</th><th>Failed</th><th>Skipped</th><th>Status</th></tr></thead>
  <tbody>{''.join(module_rows) or '<tr><td colspan="6">No tests collected.</td></tr>'}</tbody></table>
  {fail_table}
  <h2>Test case reports</h2>
  <table><thead><tr><th>Test</th><th>Area</th><th>Result</th><th>Duration</th><th>Reason</th></tr></thead>
  <tbody>{''.join(test_rows) or '<tr><td colspan="5">No tests.</td></tr>'}</tbody></table>
  <footer>Run folder: reports/runs/{_esc(_run_id)} · History: reports/index.html</footer>
</main>
</body></html>"""
