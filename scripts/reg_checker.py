import pandas as pd
import time
import os
import re
import argparse
from datetime import datetime
import difflib
import logging
from collections import deque

from constants import *

from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import bot.w3_automaton as w3auto
import bot_step2 as svl

this_report = [['Documento', 'Fecha de ingreso', 'Registrado']]

def clean_text(text):
    if isinstance(text, str):
        return re.sub(r'[^0-9a-zA-Z\s]', '', text).strip()
    return text

def process_doc(doc):
    doc = str(doc)
    if doc.isdigit():
        return str(int(doc))
    else:
        return str(doc)
    
def just_register_employee(driver, auth, emp):
    driver.send_doc_by_type("//select[@class='form-control' and @name='v_codtdocide' and @id='v_codtdocide']", 
                                "//input[@type='text' and @name='v_codtra' and @id='v_codtra']", 
                                'DNI', emp[CKEY_DOC], enter=True)
    if driver.accept_alert():
        return

    driver.click_element("//input[@name='v_flgreing' and @value='N']")
    driver.click_element("//input[@name='v_flgcontseg' and @value='N']")

    date_value = auth[AUTH_SVL_CONSTANTS][AUTH_INS_DATE]
    if date_value is None:
        date_value = driver.attr_from_element("//input[@type='text' and @name='d_fecing']", 'value')
    if len(date_value) == 0:
        logging.warning('Can not find entry insurance date')
        driver.reload_page()
        return

    driver.write_in_element("//input[@type='text' and @name='d_fecasetra']", date_value)
    driver.write_in_element("//input[@type='text' and @name='n_monrem']", auth[AUTH_SVL_CONSTANTS][AUTH_SALARY])

    driver.click_element("//a[text()='Grabar']")

    driver.accept_alert()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RoBot: Seguro Vida Ley.')
    parser.add_argument('auth_file', type=str, help='Path to the authentication JSON (RUC, Password, ...)')
    parser.add_argument('data', type=str, help='Path to the excel file')

    args = parser.parse_args()

    auth = w3auto.load_json(args.auth_file)

    if auth is not None:
        emps = pd.read_excel(args.data)

        emps[CKEY_DOC] = emps['DOCUMENTO_IDENTIDAD'].apply(lambda x: process_doc(x.split(' - ')[1]))

        filter = emps["FECHA_INGRESO"] >= pd.Timestamp("2024-03-01")
        femps = emps.loc[filter]

        driver = w3auto.WebDriverExtended(auth[AUTH_WEBDRIVER][AUTH_BROWSER], 
                                        auth[AUTH_WEBDRIVER][AUTH_HEADLESS])

        driver.url(auth[AUTH_URL])
        driver.write_in_element("//input[@id='txtRuc']", auth[AUTH_CREDENTIALS][AUTH_RUC])
        driver.write_in_element("//input[@id='txtUsuario']", auth[AUTH_CREDENTIALS][AUTH_USER])
        driver.write_in_element("//input[@id='txtContrasena']", auth[AUTH_CREDENTIALS][AUTH_PASSWORD])
        driver.click_element("//button[text()='Entrar']")
        driver.click_element("//area[@shape='rect' and @coords='250,20,464,68']")
        driver.select_in_element("//select[@name='v_ruc_ase' and @class='form-control']", 'PACIFICO COMPAÑIA DE SEGUROS Y REASEGUROS')
        driver.click_element("//a[text()='Buscar']")
        driver.click_newest_insurance("//table[@border='2' and @id='lstSeguro' and @class='forsat']")
        driver.click_element("//a[text()='Altas/Bajas actualización']")

        for idx, emp in femps.iterrows():

            if svl.employee_is_already_registered(driver,  emp[CKEY_DOC], 'DNI'):
                this_report.append([f"DNI - {svl.format_document(emp[CKEY_DOC], 'DNI')}", emp['FECHA_INGRESO'], 'Sí'])
            else:
                this_report.append([f"DNI - {svl.format_document(emp[CKEY_DOC], 'DNI')}", emp['FECHA_INGRESO'], 'No'])
                just_register_employee(driver, auth, emp)

        regse = pd.DataFrame(this_report[1:], columns=this_report[0]) 

        with pd.ExcelWriter('temp/reporte_registrados.xlsx') as writer:
            regse.to_excel(writer, sheet_name='Titulares asegurados', index=False)