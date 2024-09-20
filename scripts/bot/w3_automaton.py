import time, logging

import scripts.bot.errors as errors

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import *

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.service import Service as SafariService

def add_method_to_class(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator
    
def create_webdriver(browser_name, headless=False):
    """Create a WebDriver instance based on the specified browser."""
    driver_options = None
    service = None

    if browser_name.lower() == 'chrome':
        driver_options = ChromeOptions()
        service = ChromeService()
    elif browser_name.lower() == 'edge':
        driver_options = EdgeOptions()
        service = EdgeService()
    elif browser_name.lower() == 'firefox':
        driver_options = FirefoxOptions()
        service = FirefoxService()
    elif browser_name.lower() == 'safari':
        service = SafariService()
    else:
        raise ValueError("Unsupported browser: {}".format(browser_name))

    # Common options for all browsers
    driver_options.add_argument("--start-maximized")
    driver_options.add_argument("--log-level=OFF")

    # Set headless mode if specified
    if headless:
        if browser_name.lower() == 'chrome':
            driver_options.add_argument("--headless")
        elif browser_name.lower() == 'edge':
            driver_options.add_argument("--headless")
        elif browser_name.lower() == 'firefox':
            driver_options.add_argument("--headless")

    # Return the appropriate WebDriver instance
    if browser_name.lower() == 'chrome':
        return webdriver.Chrome(service=service, options=driver_options)
    elif browser_name.lower() == 'edge':
        return webdriver.Edge(service=service, options=driver_options)
    elif browser_name.lower() == 'firefox':
        return webdriver.Firefox(service=service, options=driver_options)
    elif browser_name.lower() == 'safari':
        return webdriver.Safari(service=service)
    
class WebDriverExtended:
    def __init__(self, browser_name, headless, timeout_wait=20) -> None:
        try:
            self.driver = create_webdriver(browser_name, headless)
            self.wait = WebDriverWait(self.driver, timeout_wait)
        except ValueError as e:
            errors.conserr(e)
            
    def close_all(self):
        remaining_windows = len(self.driver.window_handles)
        while remaining_windows > 0:
            self.driver.close()
            remaining_windows -= 1
            self.wait.until(EC.number_of_windows_to_be(remaining_windows))

    def quit(self):
        self.driver.quit()

    def url(self, url):
        self.driver.get(url)
        self.wait_page()

    def reload_page(self):
        self.driver.refresh()
        self.wait_page()

    def accept_alert(self, timeout=0.2):
        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            text = alert.text
            logging.warning(f"[!]ALERT: [\"{text}\"]")
            alert.accept()

            return True, text
        
        except TimeoutException:
            return False, None

        except NoAlertPresentException:
            return False, None

    def press_key(self, element: WebElement, mykey: Keys):
        time.sleep(0.2)
        element.send_keys(mykey)
        time.sleep(0.1)

    def attr_from_element(self, xpath: str, attr:str):
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        return element.get_attribute(attr)

    def write_in_element(self, xpath: str, input):
        element = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        self.driver.execute_script(f"arguments[0].value = '{input}';", element)
        return element

    def click_element(self, xpath: str):
        self.wait_page()
        element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        element.click()
        return element

    def select_in_element(self, xpath: str, option: str, ignore_selection: bool = False):
        element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        if not ignore_selection:
            self.wait.until(EC.presence_of_element_located((By.XPATH, f"//option[text()='{option}']")))
            select = Select(element)
            select.select_by_visible_text(option)

        return element
    
    def pick_table_as_element(self, xpath: str, slice_tag: str):
        table = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        element = table.find_element(By.TAG_NAME, slice_tag)
        return element

    def wait_page(self):
        try:
            self.wait.until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException as e:
            errors.conserr(e)

    def close_page(self):
        self.driver.close()

    def pick_window(self, index, windows):
        try:
            if index >= windows:
                raise NoSuchWindowException()
            
            self.wait.until(EC.number_of_windows_to_be(windows))

            av_windows = self.driver.window_handles
            self.driver.switch_to.window(av_windows[index])
            self.wait_page()

        except (TimeoutException, IndexError, 
                NoSuchWindowException, WebDriverException) as e:
            errors.conserr(e)
