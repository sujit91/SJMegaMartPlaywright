# SJ MegaMart Playwright Python Framework

End-to-end UI automation for [SJ MegaMart](https://sujitjena90.github.io/SujitTestingAutomation/) using **Playwright + Python + Pytest** and the **Page Object Model**.

Designed for Jenkins CI: smoke first, then full regression (~100 tests covering login through payment).

## Stack

- Python 3.10+
- Playwright (Chromium)
- Pytest + pytest-playwright + pytest-html
- Page Object Model (`pages/`)
- Jenkinsfile (Windows `bat` steps)

## Layout

```
config/          # URL, timeouts, test data
pages/           # POM classes
tests/           # 100 pytest cases
utils/           # cart helpers
Jenkinsfile      # CI pipeline
pytest.ini       # markers and defaults
```

## Setup

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

In PyCharm set the interpreter to `.venv\Scripts\python.exe` (not the global Python 3.13). Global Python does not have pytest-html / pytest-playwright.
```

## Run

```bat
pytest tests --browser chromium
pytest tests -m smoke --browser chromium
pytest tests --html=reports/report.html --self-contained-html

Local runs open a visible Chromium window (`HEADLESS` defaults to `false`). Set `HEADLESS=true` for CI or headless mode.

## Reports

Every pytest run writes files under `reports/` (folder is gitignored):

| File | Audience |
| --- | --- |
| `reports/management-report.html` | Management – pass rate, GO/NO-GO, steps, failed-step screenshots, video on fail |
| `reports/report.html` | QA – detailed pytest-html with steps, screenshots and video |
| `reports/artifacts/` | Playwright videos (`video.webm`) and failure screenshots |
| `reports/junit.xml` | Jenkins / CI |

Failed steps are screenshotted automatically. Video is kept **on failure** (`--video retain-on-failure`). Record every test with `--video on`. Zip the whole `reports` folder if you send videos with the HTML.

Open the management report after a run:

```bat
start reports\management-report.html
```
```

Base URL (override with env `BASE_URL`):

`https://sujitjena90.github.io/SujitTestingAutomation/`

Demo login: **admin / admin**

## Markers

| Marker | Use |
| --- | --- |
| smoke | Critical path |
| auth | Login / signup |
| catalog | Listing and search |
| cart | Cart |
| checkout | Address and payment |
| ui | Navigation |

## Jenkins

Point a Freestyle/Pipeline job at this repo. The `Jenkinsfile` creates a venv, installs browsers, runs smoke then regression, and publishes the management report, detailed HTML report, and JUnit results from `reports/`.
