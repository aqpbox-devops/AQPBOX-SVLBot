import pandas as pd
import json
import time
import sys
import argparse
from datetime import datetime
import difflib
import logging

from enum import Enum, auto
from __init__ import *

from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

import bot.w3_automaton as w3auto

class TimeSessionUnexpectedExpiration(Exception):
    def __init__(self, message="The current session has expired. Return to login again."):
        self.message = message
        super().__init__(self.message)

@w3auto.add_method_to_class(w3auto.WebDriverExtended)
def click_newest_insurance(self, xpath):
    body = self.pick_table_as_element(xpath, 'tbody')

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

@w3auto.add_method_to_class(w3auto.WebDriverExtended)
def send_doc_by_type(self, xpath_t, xpath_n, doc_t, doc_n, enter=True):
    """
    This function sends the document to RENIEC
    """
    full_name_doc = ID_DOC_TYPES[doc_t]['full name']
    self.select_in_element(xpath_t, full_name_doc)
    doc_input = self.write_in_element(xpath_n, str(doc_n).zfill(ID_DOC_TYPES[doc_t]['len']))
    
    if enter:
        self.press_key(doc_input, Keys.RETURN)

@w3auto.add_method_to_class(w3auto.WebDriverExtended)
def closest_match_from_element(self, xpath: str, to_match: str, bias=0.8):

    time.sleep(0.15)

    select_element = self.select_in_element(xpath, to_match, ignore_selection=True)
    
    options = [option.text for option in select_element.find_elements(By.TAG_NAME, 'option')]

    closest_match = difflib.get_close_matches(to_match, options, n=1, cutoff=bias)

    if closest_match:
        self.select_in_element(xpath, closest_match[0])

def from_login2sign_up_employee(driver: w3auto.WebDriverExtended, auth, emps, bens):

    flag = True

    while flag:
        flag = False
        driver.url(auth['url'])
        driver.write_in_element("//input[@id='txtRuc']", auth['ruc'])
        driver.write_in_element("//input[@id='txtUsuario']", auth['usr'])
        driver.write_in_element("//input[@id='txtContrasena']", auth['psw'])
        driver.click_element("//button[text()='Entrar']")
        driver.click_element("//area[@shape='rect' and @coords='250,20,464,68']")
        driver.select_in_element("//select[@name='v_ruc_ase' and @class='form-control']", 'PACIFICO COMPAÑIA DE SEGUROS Y REASEGUROS')
        driver.click_element("//a[text()='Buscar']")
        driver.click_newest_insurance("//table[@border='2' and @id='lstSeguro' and @class='forsat']")
        driver.click_element("//a[text()='Altas/Bajas actualización']")

        try:

            for index, emp in emps.iterrows():
                sign_up_employee(driver, auth, emp, bens)
        
        except TimeSessionUnexpectedExpiration:
            flag = True

def sign_up_employee(driver: w3auto.WebDriverExtended, auth, emp, bens):

    try:
        driver.send_doc_by_type("//select[@class='form-control' and @name='v_codtdocide' and @id='v_codtdocide']", 
                                "//input[@type='text' and @name='v_codtra' and @id='v_codtra']", 
                                emp[CKEY_DOC_TYPE], emp[CKEY_DOC], enter=True)
        driver.click_element("//input[@name='v_flgreing' and @value='N']")
        driver.click_element("//input[@name='v_flgcontseg' and @value='N']")

        if auth['insurance date'] is not None:
            date_value = auth['insurance date']
        else:
            date_value = driver.attr_from_element("//input[@type='text' and @name='d_fecing']", 'value')

        if len(date_value) == 0:
            logging.warning('Can not find entry insurance date')
            driver.reload_page()
            return

        driver.write_in_element("//input[@type='text' and @name='d_fecasetra']", date_value)
        driver.write_in_element("//input[@type='text' and @name='n_monrem']", auth['const salary'])

        driver.click_element("//a[text()='Grabar']")

        driver.accept_alert()

        selected_bens = bens.loc[bens[CKEY_PK] == emp[CKEY_DOC]]

        return search_beneficier_by_doc(driver, auth, emp, selected_bens)
    except ValueError:
        raise TimeSessionUnexpectedExpiration()

def search_beneficier_by_doc(driver: w3auto.WebDriverExtended, auth, emp, bens):

    try:
        driver.write_in_element("//input[@type='text' and @name='v_codtrabus']", emp[CKEY_DOC])
        
        driver.click_element("//a[@href='javascript:buscarTraLisBD();']")

        body = driver.pick_table_as_element("//table[@border='2' and @id='lstPolizaTrabajador']", 'tbody')
        if list(body.find_elements(By.TAG_NAME, 'tr'))[0].get_attribute('class') != 'empty':
            driver.click_element("//a[img[@title='Ingresar Beneficiario(s)']]")
            driver.pick_window(1)

            logging.info(f"<EMP {emp[CKEY_DOC_TYPE]}({emp[CKEY_DOC]}): #bens({len(bens)})>")

            #input()

            for index, ben in bens.iterrows():
                registered = is_adult_question(driver, auth, emp, ben)
                logging.info(f"|* <BEN {ben[CKEY_DOC_TYPE]}({ben[CKEY_DOC]}): REGISTERED({registered}), REASON({None})>")

            return close_beneficier_page(driver, auth, emp, ben)
        return
    except ValueError:
        raise TimeSessionUnexpectedExpiration()

def is_adult_question(driver: w3auto.WebDriverExtended, auth, emp, ben) -> bool:
    try:
        if ben[CKEY_ISADULT]:
            return insert_just_doc(driver, auth, emp, ben)
        else:
            return insert_full_form(driver, auth, emp, ben)
    except ValueError:
        raise TimeSessionUnexpectedExpiration()
    
def insert_just_doc(driver: w3auto.WebDriverExtended, auth, emp, ben) -> bool:
    try:
        driver.click_element("//input[@name='answer' and @value='no']")
        driver.send_doc_by_type("//select[@name='v_codtdocideben' and @id='v_codtdocideben']",
                                "//input[@type='text' and @name='v_codben' and @id='v_codben']",
                                ben[CKEY_DOC_TYPE], ben[CKEY_DOC], enter=True)
        if driver.accept_alert():
            return False
        
        return save_beneficier_data(driver, auth, emp, ben)
    except ValueError:
        raise TimeSessionUnexpectedExpiration()

def insert_full_form(driver: w3auto.WebDriverExtended, auth, emp, ben) -> bool:

    try:
        driver.click_element("//input[@name='answer' and @value='yes']")
        driver.send_doc_by_type("//select[@name='v_codtdocideben' and @id='v_codtdocideben']", 
                                "//input[@type='text' and @name='v_codben' and @name='v_codben']",
                                ben[CKEY_DOC_TYPE], ben[CKEY_DOC], enter=False)
        
        #Bad format input or Missed data in RENIEC => Can not do for this beneficier
        if driver.accept_alert():
            return False

        driver.write_in_element("//input[@type='text' and @name='v_apepatben' and @id='v_apepatbenID']", ben[CKEY_APPA])
        driver.write_in_element("//input[@type='text' and @name='v_apematben' and @id='v_apematbenID']", ben[CKEY_APMA])
        driver.write_in_element("//input[@type='text' and @name='v_nomben' and @id='v_nombenID']", ben[CKEY_NAME])
        driver.write_in_element("//input[@type='text' and @name='d_fecnacben' and @id='d_fecnacben']", ben[CKEY_BDATE])
        driver.write_in_element("//input[@type='text' and @name='v_direccion' and @id='v_direccionID']", ben[CKEY_ADDR])

        driver.closest_match_from_element("//select[@name='v_coddepBen' and @id='v_coddepBen']", ben[CKEY_DEP])
        driver.closest_match_from_element("//select[@name='v_codproBen' and @id='v_codproBen']", ben[CKEY_PROV])
        driver.closest_match_from_element("//select[@name='v_coddisBen' and @id='v_coddisBen']", ben[CKEY_DIST])
        
        if ben[CKEY_SEX] in LGENDER_VARS:
            driver.click_element("//input[@type='radio' and @name='v_genben' and @value='M']")
        else:
            driver.click_element("//input[@type='radio' and @name='v_genben' and @value='F']")

        return save_beneficier_data(driver, auth, emp, ben)
    except ValueError:
        raise TimeSessionUnexpectedExpiration()

def save_beneficier_data(driver: w3auto.WebDriverExtended, auth, emp, ben) -> bool:

    try:
        driver.select_in_element("//select[@name='n_codvinfam' and @class='form-control']", ben[CKEY_REL])

        driver.click_element("//a[text()='Grabar']")

        driver.accept_alert()

        return True

    except ValueError:
        raise TimeSessionUnexpectedExpiration()

def close_beneficier_page(driver: w3auto.WebDriverExtended, auth, emp, ben):
    
    try:
        driver.click_element("//a[text()='Regresar']")
        driver.pick_window(0)
    except ValueError:
        raise TimeSessionUnexpectedExpiration()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RoBot: Seguro Vida Ley.')
    parser.add_argument('auth_file', type=str, help='Path to the authentication JSON (RUC, Password, ...)')

    args = parser.parse_args()

    auth = w3auto.load_json(args.auth_file)

    if auth is not None:
        try:
            driver = w3auto.WebDriverExtended(auth['webdriver']['browser'], 
                                            auth['webdriver']['headless'])
        except ValueError as e:
            w3auto.conserr(e)
            exit(0)

        emps = pd.read_csv(SHAREGS_PARSED_EMPLOYEES)
        bens = pd.read_csv(SHAREGS_PARSED_BENEFICIERS)

        w3auto.setup_logging(SHAREGS_INFO_LOGS, SHAREGS_WARNING_LOGS)

        from_login2sign_up_employee(driver, auth, emps, bens)
