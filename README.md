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
```

## Run

```bat
pytest tests --browser chromium
pytest tests -m smoke --browser chromium
pytest tests --html=reports/report.html --self-contained-html
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

Point a Freestyle/Pipeline job at this repo. The `Jenkinsfile` creates a venv, installs browsers, runs smoke then regression, and publishes JUnit + HTML reports under `reports/`.
