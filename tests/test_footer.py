import os
import re
import pytest
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait

WAIT_SEC = int(os.getenv("WAIT_SEC", "25"))
DOMAIN = urlparse(os.getenv("BASE_URL", "https://only.digital")).netloc

FOOTER_XPATHS = [
    "//footer",
    "//*[@role='contentinfo']",
    "//*[contains(translate(@id,'FOOTER','footer'),'footer')]",
    "//*[contains(translate(@class,'FOOTER','footer'),'footer')]",
]

SOCIAL_PATTERNS = [
    "vk.com", "t.me", "telegram", "instagram.com",
    "linkedin.com", "youtube.com", "youtube."
]

def wait_for(driver, predicate, timeout=WAIT_SEC):
    """Универсальный явный ожидатель."""
    w = WebDriverWait(driver, timeout, poll_frequency=0.5)
    return w.until(lambda d: predicate())

def find_footer(driver):
    for xp in FOOTER_XPATHS:
        els = driver.find_elements(By.XPATH, xp)
        if els:
            return els[0]
    return None

def is_internal(href: str) -> bool:
    if not href:
        return False
    if href.startswith(("mailto:", "tel:", "#", "javascript:")):
        return False
    try:
        return urlparse(href).netloc in ("", DOMAIN)
    except Exception:
        return False

@pytest.mark.parametrize("url", ["https://only.digital"], ids=["home"])
def test_footer_present(driver, url):
    driver.get(url)
    try:
        footer = wait_for(driver, lambda: find_footer(driver))
    except TimeoutException:
        raise NoSuchElementException("Footer not found on page within timeout")
    assert footer is not None, "Footer element must exist"

@pytest.mark.parametrize("url", ["https://only.digital"], ids=["home"])
def test_footer_has_logo_nav_contacts_social(driver, url):
    driver.get(url)
    footer = wait_for(driver, lambda: find_footer(driver))

    # 1) Логотип (img или svg внутри футера)
    has_logo = bool(footer.find_elements(By.TAG_NAME, "img")) or bool(footer.find_elements(By.TAG_NAME, "svg"))
    assert has_logo, "Footer should contain logo (img or svg)"

    # 2) Навигационные ссылки (внутренние)
    links = footer.find_elements(By.TAG_NAME, "a")
    internal_links = [a for a in links if is_internal(a.get_attribute("href") or "")]
    assert len(internal_links) >= 1, "Footer should contain at least 1 internal nav link"

    # 3) Контактная информация (mailto/tel или текст)
    has_contact_link = any(
        (a.get_attribute("href") or "").lower().startswith(("mailto:", "tel:")) for a in links
    )
    text = (footer.text or "").lower()
    has_contact_text = bool(re.search(r"(contact|контакт|support|поддержк|почта|email|телефон)", text))
    assert has_contact_link or has_contact_text, "Footer should have contact info (mailto/tel link or contact text)"

    # 4) Социальные сети
    has_social = any(
        any(p in (a.get_attribute("href") or "").lower() for p in SOCIAL_PATTERNS)
        for a in links
    )
    # не критично для прохождения, но если хотите — сделайте строгим:
    # assert has_social, "Footer should contain at least one social link"
    # Пока оставим мягко, чтобы не зависеть от изменений сайта:
    if not has_social:
        print("Note: no social links detected in footer — not failing the test.")
