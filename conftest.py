import os
import re
import pathlib
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

BASE_URL = os.getenv("BASE_URL", "https://only.digital").strip()

@pytest.fixture(scope="session")
def pages():
    """
    Список страниц для проверки.
    По умолчанию — только главная (устойчиво для CI).
    Можно передать env PAGES="https://only.digital,https://only.digital/services"
    """
    raw = os.getenv("PAGES", "").strip()
    if raw:
        lst = [u.strip() for u in raw.split(",") if u.strip()]
        return lst
    return [BASE_URL]

@pytest.fixture(scope="session")
def driver():
    """Chrome в headless-режиме с Selenium Manager (без ручного драйвера)."""
    caps = DesiredCapabilities().CHROME
    caps["goog:loggingPrefs"] = {"browser": "ALL"}

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    drv = webdriver.Chrome(options=options, desired_capabilities=caps)
    yield drv
    drv.quit()

# ---------- Скриншот при падении ----------
def _safe_name(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9\-_.]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "page"

@pytest.fixture(autouse=True)
def screenshot_on_failure(request, driver):
    yield
    rep = getattr(request.node, "rep_call", None)
    if rep and rep.failed:
        page = None
        if hasattr(request.node, "callspec"):
            page = request.node.callspec.params.get("url", None)
        fname = _safe_name(page) if page else "page"
        out_dir = pathlib.Path("reports") / "screenshots"
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            driver.save_screenshot(str(out_dir / f"failed_{fname}.png"))
        except Exception:
            pass

def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
