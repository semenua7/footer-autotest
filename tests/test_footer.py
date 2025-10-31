
import re
import pytest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

FOOTER_XPATHS = [
    "//footer",
    "//*[@role='contentinfo']",
    "//*[contains(translate(@id,'FOOTER','footer'),'footer')]",
    "//*[contains(translate(@class,'FOOTER','footer'),'footer')]",
]

def find_footer(driver):
    for xp in FOOTER_XPATHS:
        els = driver.find_elements(By.XPATH, xp)
        if els:
            return els[0]
    raise NoSuchElementException("Footer element not found by any known locator.")

def has_policy_or_contacts(footer):
    # Поиск по тексту и по ссылке
    text = footer.text or ""
    if re.search(r"политик|privacy|confidential|конфиденц", text, re.IGNORECASE):
        return True
    # href
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
    socials = ["vk.com", "t.me", "telegram", "instagram.com", "linkedin.com", "youtube.com", "youtube." ]
    for a in links:
        href = (a.get_attribute("href") or "").lower()
        if any(s in href for s in socials):
            return True
        if href.startswith("mailto:") or href.startswith("tel:"):
            return True
    return False

@pytest.mark.parametrize("url", [], ids=[])
def test_placeholder():
    # Заглушка, чтобы pytest не ругался без параметров в коллекции
    assert True

def pytest_generate_tests(metafunc):
    if "url" in metafunc.fixturenames:
        pages = metafunc.config._fixturemanager.getfixturedefs("pages", metafunc.module)[0].func()
        metafunc.parametrize("url", pages, ids=pages)

def test_footer_present(driver, url):
    driver.get(url)
    footer = find_footer(driver)
    assert footer is not None, "Footer should exist on the page"

def test_footer_has_links_and_text(driver, url):
    driver.get(url)
    footer = find_footer(driver)
    links = footer.find_elements(By.TAG_NAME, "a")
    assert len(links) >= 1, "Footer should have at least one link"
    text = (footer.text or "").strip()
    assert len(text) >= 20, "Footer text should not be empty (>= 20 symbols)"

def test_footer_has_policy_or_contacts(driver, url):
    driver.get(url)
    footer = find_footer(driver)
    assert has_policy_or_contacts(footer), "Footer should contain policy/privacy or contacts link/text"

def test_footer_has_social_or_contacts(driver, url):
    driver.get(url)
    footer = find_footer(driver)
    assert has_social_or_contacts(footer), "Footer should contain at least one social or contact link (mailto/tel)"
