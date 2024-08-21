import pandas as pd
import json
import sys
import argparse
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

try:
    driver = webdriver.Chrome()
except WebDriverException as e:
    print(f"ERROR:[{e}]", file=sys.stderr)

def load_json(file):
    try:
        with open(file, 'r', encoding='utf-8') as F:
            data = json.load(F)
            return data
    except FileNotFoundError as e:
        print(f"ERROR:[{e}]", file=sys.stderr)
    except json.JSONDecodeError as e:
        print(f"ERROR:[{e}]", file=sys.stderr)
    return None
    
def write_in_element(xpath, input, timeout=10):
    element = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    driver.execute_script(f"arguments[0].value = '{input}';", element)

def click_element(xpath, timeout=10):
    element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    element.click()

def select_in_element(xpath, option, timeout=10):
    element = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    select = Select(element)
    WebDriverWait(driver, timeout).until(
        lambda s: option in [o.text for o in select.options]
    )
    select.select_by_visible_text(option)

def click_newest_insurance(xpath, timeout=10):
    insurance_table = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, xpath)))

    body = insurance_table.find_element(By.TAG_NAME, 'tbody')

    current_date = datetime.now()

    closest_date_diff = None
    closest_check = None

    for row in list(body.find_elements(By.TAG_NAME, 'tr')):
        cols = row.find_elements(By.TAG_NAME, 'td')

        check = cols[0]
        start_date =  datetime.strptime(cols[3].text.strip(), "%d/%m/%Y")

        date_diff = abs((start_date - current_date).days)

        if closest_date_diff is None or date_diff < closest_date_diff:
            closest_date_diff = date_diff
            closest_check = check
        
    closest_check.click()

def wait_page(timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except TimeoutException as e:
        print(f"ERROR:[{e}]", file=sys.stderr)
    
if __name__ == '__main__':

    auth = load_json('../credentials.json')

    driver.get(auth['url'])
    write_in_element('//input[@id="txtRuc"]', auth['ruc'])
    write_in_element('//input[@id="txtUsuario"]', auth['usr'])
    write_in_element('//input[@id="txtContrasena"]', auth['psw'])
    click_element('//button[text()="Entrar"]')
    click_element('//area[@shape="rect" and @coords="250,20,464,68"]')
    select_in_element('//select[@name="v_ruc_ase" and @class="form-control"]', 'PACIFICO COMPAÑIA DE SEGUROS Y REASEGUROS')
    click_element('//a[text()="Buscar"]')
    click_newest_insurance('//table[@border="2" and @id="lstSeguro" and @class="forsat"]')
    click_element('//a[text()="Altas/Bajas actualización"]')
    input()
