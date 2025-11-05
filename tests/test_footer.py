import os
import re
import pytest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

# ---------- Параметризация страниц без хитростей ----------
# Берём список страниц из ENV PAGES (через запятую) или BASE_URL (по умолчанию главная)
def _get_pages():
    pages_env = os.getenv("PAGES", "").strip()
    if pages_env:
        lst = [u.strip() for u in pages_env.split(",") if u.strip()]
        return lst if lst else ["https://only.digital"]
    base = os.getenv("BASE_URL", "https://only.digital").strip()
    return [base]

PAGES = _get_pages()

# ---------- Утилиты для поиска футера ----------
FOOTER_XPATHS = [
    "//footer",
    "//*[@role='contentinfo']",
    "//*[contains(translate(@id,'FOOTER','footer'),'footer')]",
    "//*[contains(translate(@class,'FOOTER','footer'),'footer')]",
]

def _try_find_footer(driver):
    for xp in FOOTER_XPATHS:
        els = driver.find_elements(By.XPATH, xp)
        if els:
            return els[0]
    return None

def wait_for_footer(driver, timeout=25):
    wait = WebDriverWait(driver, timeout=timeout, poll_frequency=0.5)
    try:
        return wait.until(lambda d: _try_find_footer(d))
    except TimeoutException:
        raise NoSuchElementException("Footer element not found after wait")

def has_policy_or_contacts(footer):
    text = footer.text or ""
    if re.search(r"политик|privacy|confidential|конфиденц", text, re.IGNORECASE):
        return True
    links = footer.find_elements(By.TAG_NAME, "a")
    for a in links:
        href = (a.get_attribute("href") or "").lower()
        if any(k in href for k in ["policy", "privacy", "confidential"]):
            return True
        if re.search(r"контакт|contact", (a.text or ""), re.IGNORECASE):
            return True
    return False

def has_social_or_contacts(footer):
    links = footer.find_elements(By.TAG_NAME, "a")
    socials = ["vk.com", "t.me", "telegram", "instagram.com", "linkedin.com", "youtube.com", "youtube."]
    for a in links:
        href = (a.get_attribute("href") or "").lower()
        if any(s in href for s in socials):
            return True
        if href.startswith("mailto:") or href.startswith("tel:"):
            return True
    return False

# ---------- Тесты ----------
@pytest.mark.parametrize("url", PAGES, ids=PAGES)
def test_footer_present(driver, url):
    driver.get(url)
    footer = wait_for_footer(driver, timeout=25)
    assert footer is not None, "Footer should exist on the page"

@pytest.mark.parametrize("url", PAGES, ids=PAGES)
def test_footer_has_links_and_text(driver, url):
    driver.get(url)
    footer = wait_for_footer(driver, timeout=25)
    links = footer.find_elements(By.TAG_NAME, "a")
    assert len(links) >= 1, "Footer should have at least one link"
    text = (footer.text or "").strip()
    assert len(text) >= 10, "Footer text should not be empty (>= 10 symbols)"

@pytest.mark.parametrize("url", PAGES, ids=PAGES)
def test_footer_has_policy_or_contacts(driver, url):
    driver.get(url)
    footer = wait_for_footer(driver, timeout=25)
    assert has_policy_or_contacts(footer), "Footer should contain policy/privacy or contacts link/text"

@pytest.mark.parametrize("url", PAGES, ids=PAGES)
def test_footer_has_social_or_contacts(driver, url):
    driver.get(url)
    footer = wait_for_footer(driver, timeout=25)
    assert has_social_or_contacts(footer), "Footer should contain at least one social or contact link (mailto/tel)"
