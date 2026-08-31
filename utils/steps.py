"""Capture Playwright actions as report steps with failure screenshots."""

from __future__ import annotations

import re
import time
from contextvars import ContextVar
from pathlib import Path

SCREENSHOT_DIR = Path("reports") / "screenshots"
_steps: ContextVar[list[dict]] = ContextVar("sj_steps")
_installed = False


def reset_steps() -> None:
    _steps.set([])


def get_steps() -> list[dict]:
    try:
        return list(_steps.get())
    except LookupError:
        return []


def add_step(name: str, status: str = "passed", screenshot: str | None = None, error: str = "") -> None:
    try:
        steps = _steps.get()
    except LookupError:
        steps = []
        _steps.set(steps)
    steps.append(
        {
            "name": name,
            "status": status,
            "screenshot": screenshot,
            "error": error,
        }
    )


def take_screenshot(page: Page, label: str) -> str | None:
    try:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^\w.-]+", "_", label)[:80]
        path = SCREENSHOT_DIR / f"{int(time.time() * 1000)}_{safe}.png"
        page.screenshot(path=str(path), full_page=True)
        return str(path)
    except Exception:
        return None


def _selector_of(locator: Locator) -> str:
    for attr in ("_selector", "selector"):
        value = getattr(locator, attr, None)
        if isinstance(value, str) and value:
            return value
    text = str(locator)
    match = re.search(r"selector=['\"]([^'\"]+)", text)
    return match.group(1) if match else text[:100]


def _run(name: str, fn, page: Page | None):
    try:
        result = fn()
        add_step(name, "passed")
        return result
    except Exception as exc:
        shot = take_screenshot(page, name) if page is not None else None
        add_step(name, "failed", screenshot=shot, error=str(exc)[:400])
        raise


def _wrap_locator(original, action: str):
    def wrapped(self: Locator, *args, **kwargs):
        selector = _selector_of(self)
        if action == "Fill":
            raw = args[0] if args else kwargs.get("value", "")
            shown = "********" if re.search(r"password|otp|cvv", selector, re.I) else raw
            name = f"{action} {selector} = {shown!r}"
        else:
            name = f"{action} {selector}"
        return _run(name, lambda: original(self, *args, **kwargs), self.page)

    return wrapped


def _wrap_goto(original):
    def wrapped(self: Page, url: str, **kwargs):
        return _run(f"Open {url}", lambda: original(self, url, **kwargs), self)

    return wrapped


def _wrap_reload(original):
    def wrapped(self: Page, **kwargs):
        return _run("Reload page", lambda: original(self, **kwargs), self)

    return wrapped


def install_action_hooks() -> None:
    global _installed
    if _installed:
        return
    from playwright.sync_api import Locator, Page

    Locator.click = _wrap_locator(Locator.click, "Click")
    Locator.fill = _wrap_locator(Locator.fill, "Fill")
    Locator.hover = _wrap_locator(Locator.hover, "Hover")
    Locator.press = _wrap_locator(Locator.press, "Press")
    Locator.check = _wrap_locator(Locator.check, "Check")
    Locator.select_option = _wrap_locator(Locator.select_option, "Select")
    Page.goto = _wrap_goto(Page.goto)
    Page.reload = _wrap_reload(Page.reload)
    _installed = True
