import json
import sys
import os
import time
import logging
import inspect

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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

def setup_logging(debug_info_log, warning_error_log):
    sys.stderr = open(os.devnull, 'w')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    info_handler = logging.FileHandler(debug_info_log)
    info_handler.setLevel(logging.INFO)

    warning_error_handler = logging.FileHandler(warning_error_log)
    warning_error_handler.setLevel(logging.WARNING)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    info_handler.setFormatter(formatter)
    warning_error_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(info_handler)
    logger.addHandler(warning_error_handler)

    info_handler.addFilter(lambda record: record.levelno < logging.WARNING)
    warning_error_handler.addFilter(lambda record: logging.WARNING <= record.levelno <= logging.CRITICAL)
    
def conserr(e, pass_=False):
    logging.error(f"MSG: [{e}], WHERE:[{__name__}.{inspect.stack()[1].function}]", exc_info=True)
    if not pass_:
        exit(0)

def load_json(file):
    try:
        with open(file, 'r', encoding='utf-8') as F:
            data = json.load(F)
            return data
    except FileNotFoundError as e:
        conserr(e)
    except json.JSONDecodeError as e:
        conserr(e)
    return None
    
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
            conserr(e)

    def quit(self):
        self.driver.quit()

    def url(self, url):
        self.driver.get(url)
        self.wait_page()

    def reload_page(self):
        self.driver.refresh()
        self.wait_page()

    def accept_alert(self):
        try:
            time.sleep(0.15)
            alert = self.driver.switch_to.alert
            logging.warning(f"[!]ALERT: [\"{alert.text}\"]")
            alert.accept()

            return True

        except NoAlertPresentException as e:
            conserr(e, True)
            return False

    def press_key(self, element: WebElement, mykey: Keys):
        time.sleep(0.15)
        element.send_keys(mykey)
        time.sleep(0.15)

    def attr_from_element(self, xpath: str, attr:str):
        element = self.wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        return element.get_attribute(attr)

    def write_in_element(self, xpath: str, input):
        element = self.wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        self.driver.execute_script(f"arguments[0].value = '{input}';", element)
        return element

    def click_element(self, xpath: str):
        element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        element.click()
        return element

    def select_in_element(self, xpath: str, option: str, ignore_selection: bool = False):
        element = self.wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        if not ignore_selection:
            select = Select(element)
            select.select_by_visible_text(option)

        return element
    
    def pick_table_as_element(self, xpath: str, slice_tag: str):
        table = self.wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        element = table.find_element(By.TAG_NAME, slice_tag)
        return element

    def wait_page(self):
        try:
            self.wait.until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException as e:
            conserr(e)

    def close_page(self):
        self.driver.close()

    def pick_window(self, index):
        time.sleep(0.15)
        av_windows = self.driver.window_handles
        try:
            self.driver.switch_to.window(av_windows[index])
            self.wait_page()

        except IndexError as e:
            conserr(e)
        except NoSuchWindowException as e:
            conserr(e)
        except WebDriverException as e:
            conserr(e)
