import re
import pytest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

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
    wait = WebDriverWait(driver, timeout, poll_frequency=0.5)
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
