import pandas as pd
import json
import argparse
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

def load_json(file):
    try:
        with open('credentials.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"FNF: File '{file}' not found.")
        return None
    except json.JSONDecodeError:
        print("Error while trying to decode json file.")
        return None

def wait_page_loading(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("La página está completamente cargada.")
    except TimeoutException:
        print("La página no se cargó completamente en el tiempo esperado.")

def get_webdriver():
    try:
        driver = webdriver.Chrome()
    except WebDriverException:
        try:
            driver = webdriver.Edge()
        except WebDriverException:
            return None
    return driver

def main(driver, credentials):

    if driver is not None and credentials is not None:

        driver.get(credentials['url'])

        driver.find_element(By.ID, 'txtRuc').send_keys(credentials['ruc'])
        driver.find_element(By.ID, 'txtUsuario').send_keys(credentials['user'])
        driver.find_element(By.ID, 'txtContrasena').send_keys(credentials['psw'])
        driver.find_element(By.ID, 'btnAceptar').click()

        wait_page_loading(driver)

        driver.execute_script('f_segurovida();')

        wait_page_loading(driver)

        Select(driver.find_element(By.NAME, 'v_ruc_ase')).select_by_visible_text('PACIFICO COMPAÑIA DE SEGUROS Y REASEGUROS')
        driver.execute_script('buscar();')

        wait_page_loading(driver)

        insurance_table = driver.find_element(By.ID, 'lstSeguro').find_element(By.TAG_NAME, 'tbody')

        current_date = datetime.now()

        closest_date_diff = None
        closest_check = None

        for row in list(insurance_table.find_elements(By.TAG_NAME, 'tr')):
            cols = row.find_elements(By.TAG_NAME, 'td')

            check = cols[0]
            start_date =  datetime.strptime(cols[3].text.strip(), "%d/%m/%Y")

            date_diff = abs((start_date - current_date).days)

            if closest_date_diff is None or date_diff < closest_date_diff:
                closest_date_diff = date_diff
                closest_check = check
            
        closest_check.click()

        driver.execute_script('altasbajas();')

        wait_page_loading(driver)

        #EXCEL REQUEST

        driver.find_element(By.NAME, 'v_codtrabus').send_keys('75410305')
        driver.execute_script('buscarTraLisBD();')

        wait_page_loading(driver)

        input()

        driver.quit()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seguro Vida Ley WebBot.')
    parser.add_argument('credentials_file', type=str, help='Path to the credentials JSON (RUC, Password, ...)')

    args = parser.parse_args()
    main(get_webdriver(), load_json(args.credentials_file))
        