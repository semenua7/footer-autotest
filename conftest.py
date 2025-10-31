
import os
import re
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager

DEFAULT_BASE = os.getenv("BASE_URL", "https://only.digital")

def is_internal(href, base):
    if not href:
        return False
    if href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return False
    u = urlparse(urljoin(base, href))
    return u.netloc == urlparse(base).netloc

def discover_pages(base=DEFAULT_BASE, limit=5):
    pages_env = os.getenv("PAGES")
    if pages_env:
        return [u.strip() for u in pages_env.split(",") if u.strip()]
    try:
        r = requests.get(base, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        hrefs = []
        for a in soup.find_all("a"):
            href = a.get("href")
            if is_internal(href, base):
                full = urljoin(base, href)
                hrefs.append(full)
        uniq = []
        seen = set()
        for u in hrefs:
            # нормализуем, убираем якоря/квери
            p = urlparse(u)
            norm = f"{p.scheme}://{p.netloc}{p.path}"
            if norm not in seen:
                seen.add(norm)
                uniq.append(norm)
            if len(uniq) >= limit:
                break
        if base not in uniq:
            uniq.insert(0, base)
        return uniq[:limit]
    except Exception:
        return [base]

@pytest.fixture(scope="session")
def pages():
    return discover_pages()

@pytest.fixture(scope="session")
def driver():
    caps = DesiredCapabilities().CHROME
    caps["goog:loggingPrefs"] = {"browser": "ALL"}

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options, desired_capabilities=caps)
    yield driver
    driver.quit()


# --- Screenshot on failure ----------------------------------------------------
import pathlib

def _safe_name(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r'[^a-z0-9\-_.]+', '-', s)
    s = re.sub(r'-{2,}', '-', s).strip('-')
    return s or "page"

def pytest_runtest_makereport(item, call):
    # Attach test outcome to the item for later use
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

@pytest.fixture(autouse=True)
def screenshot_on_failure(request, driver):
    # Run test
    yield
    # After test: if failed, make a screenshot
    failed = getattr(request.node, "rep_call", None)
    if failed and failed.failed:
        # Try to get page url param if present
        page = "page"
        if hasattr(request.node, "callspec"):
            page = request.node.callspec.params.get("url", "page")
        fname = _safe_name(page)
        out_dir = pathlib.Path("reports") / "screenshots"
        out_dir.mkdir(parents=True, exist_ok=True)
        png_path = out_dir / f"failed_{fname}.png"
        try:
            driver.save_screenshot(str(png_path))
        except Exception:
            pass
