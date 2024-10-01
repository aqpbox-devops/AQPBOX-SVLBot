emp_registered_out = [['Documento', 'Nro. de beneficiados', 'Registrado', 'Motivo']]
ben_registered_out = [['Trabajador', 'Documento', 'Registrado', 'Motivo']]
emp_terminated_out = [['Documento', 'Cesado', 'Motivo']]

import pandas as pd
import time
import os
from datetime import datetime
import difflib
import logging
from collections import deque

from scripts.constants import *

from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import scripts.bot.w3_automaton as w3auto
import scripts.bot.errors as errors

def yesno(val: bool):
    ans = 'Sí' if val else 'No'
    return ans

def format_document(doc_n, doc_t):
    return str(doc_n).zfill(ID_DOC_TYPES[doc_t]['len'])

def fdevinfo(msg: str, max_length: int = 50, padding: str = '*') -> str:
    
    if len(msg) >= max_length:
        return msg
    padding_length = max_length - len(msg)
    padding_side = padding_length // 2
    logging.info(f"/{padding * padding_side}[{msg}]{padding * padding_side}/")

def emp_registered_log(emp, bens, registered, reason):
    fdoc_tn = f"{emp[CKEY_DOC_TYPE]} - {format_document(emp[CKEY_DOC], emp[CKEY_DOC_TYPE])}"
    len_bens = len(bens)
    logging.info(f"EMP ({fdoc_tn}): #BENEFICIERS({len_bens}), REGISTERED({registered}), REASON({reason})")
    emp_registered_out.append([fdoc_tn, len_bens, yesno(registered), reason])

def ben_registered_log(emp, ben, registered, reason):
    fdoc_tn = f"{ben[CKEY_DOC_TYPE]} - {format_document(ben[CKEY_DOC], ben[CKEY_DOC_TYPE])}"
    logging.info(f"** BEN ({fdoc_tn}): REGISTERED({registered}), REASON({reason})")
    ben_registered_out.append([f"{emp[CKEY_DOC_TYPE]} - {format_document(emp[CKEY_DOC], emp[CKEY_DOC_TYPE])}", fdoc_tn, yesno(registered), reason])

def terminated_log(emp, terminated, reason):
    fdoc_tn = f"{emp[CKEY_DOC_TYPE]} - {format_document(emp[CKEY_DOC], emp[CKEY_DOC_TYPE])}"
    logging.info(f"EMP ({fdoc_tn}): TERMINATED({terminated}), REASON({reason})")
    emp_terminated_out.append([fdoc_tn, yesno(terminated), reason])

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
        end_date = datetime.strptime(cols[4].text.strip(), "%d/%m/%Y")

        if end_date < current_date:
            return False
        
        date_diff = abs((start_date - current_date).days)

        if closest_date_diff is None or date_diff < closest_date_diff:
            closest_date_diff = date_diff
            closest_check = check
        
    closest_check.click()
    return True

@w3auto.add_method_to_class(w3auto.WebDriverExtended)
def send_doc_by_type(self, xpath_t, xpath_n, doc_t, doc_n, enter=True):
    """
    This function sends the document to RENIEC
    """
    full_name_doc = ID_DOC_TYPES[doc_t]['full name']
    self.select_in_element(xpath_t, full_name_doc)
    doc_input = self.write_in_element(xpath_n, format_document(doc_n, doc_t))
    
    if enter:
        self.press_key(doc_input, Keys.RETURN)

@w3auto.add_method_to_class(w3auto.WebDriverExtended)
def closest_match_from_element(self, xpath: str, to_match: str, bias=0.8):

    time.sleep(0.15)

    select_element = self.select_in_element(xpath, to_match, ignore_selection=True)
    
    options = [option.text for option in select_element.find_elements(By.TAG_NAME, 'option')]
    if len(options) > 1:
        options = options[1:]
    logging.info(f"<CLOSEST MATCH FOR [{to_match}]>")
    logging.info(f"\tOPTIONS: {options}")
    closest_match = difflib.get_close_matches(to_match, options, n=1, cutoff=bias)
    logging.info(f"\tCLOSEST: {closest_match}")
    if closest_match:
        self.select_in_element(xpath, closest_match[0])

def employee_is_already_registered(driver: w3auto.WebDriverExtended, doc_n, doc_t):
    driver.write_in_element("//input[@type='text' and @name='v_codtrabus']", format_document(doc_n, doc_t))
    driver.click_element("//a[@href='javascript:buscarTraLisBD();']")

    body = driver.pick_table_as_element("//table[@border='2' and @id='lstPolizaTrabajador']", 'tbody')
    unique_row = list(body.find_elements(By.TAG_NAME, 'tr'))[0]
    employee_terminated = unique_row.get_attribute('class') != 'empty'
    cells = list(unique_row.find_elements(By.TAG_NAME, 'td'))

    if len(cells) == 11:
        employee_terminated = cells[5].text != 'Baja'
    else:
        employee_terminated = False
    return employee_terminated

#EMPLOYEES AND BENEFICIERS REGISTRATION

def from_login2update_revenue_insurance(driver: w3auto.WebDriverExtended, auth, emps, bens = None, register_mode = True):

    flag = True

    all_emps = deque()
    for index, emp in emps.iterrows():
        all_emps.append(emp)

    if not all_emps:
        logging.info('No data to use.')
        return False
    
    emp = None

    while flag:
        flag = False
        driver.url(auth[AUTH_URL])
        driver.write_in_element("//input[@id='txtRuc']", auth[AUTH_CREDENTIALS][AUTH_RUC])
        driver.write_in_element("//input[@id='txtUsuario']", auth[AUTH_CREDENTIALS][AUTH_USER])
        driver.write_in_element("//input[@id='txtContrasena']", auth[AUTH_CREDENTIALS][AUTH_PASSWORD])
        driver.click_element("//button[text()='Entrar']")
        driver.click_element("//area[@shape='rect' and @coords='250,20,464,68']")
        driver.select_in_element("//select[@name='v_ruc_ase' and @class='form-control']", 'PACIFICO COMPAÑIA DE SEGUROS Y REASEGUROS')
        driver.click_element("//a[text()='Buscar']")
        if not driver.click_newest_insurance("//table[@border='2' and @id='lstSeguro' and @class='forsat']"):
            logging.info('Se requiere actualizar la poliza')
            return False
        
        driver.click_element("//a[text()='Altas/Bajas actualización']")
        try:
            if register_mode:
                while all_emps:
                    emp = all_emps.popleft()
                    if emp is not None:
                        driver.wait_page()
                        selected_bens = bens.loc[bens[CKEY_PK] == emp[CKEY_DOC]]#IMPORTANT CODE LINE!!!!!!!!
                        sign_up_employee(driver, auth, emp, selected_bens)
            else:
                while all_emps:
                    emp = all_emps.popleft()
                    if emp is not None:
                        driver.wait_page()
                        terminate_employee(driver, auth, emp)
                    
            driver.click_element("//a[text()='CERRAR SESIÓN']")
            return True
        except (ConnectionError, 
                ConnectionRefusedError, 
                ConnectionAbortedError,
                NoSuchWindowException, 
                StaleElementReferenceException,
                TimeoutException,
                UnexpectedAlertPresentException,
                ElementNotVisibleException,
                ElementNotSelectableException,
                ElementNotInteractableException,
                SessionNotCreatedException):
            flag = True
            all_emps.append(emp)
            logging.info("-- TRYING AGAIN - RESTARTING --")
            time.sleep(0.5)
            driver.close_all()

def sign_up_employee(driver: w3auto.WebDriverExtended, auth, emp, bens):

    driver.send_doc_by_type("//select[@class='form-control' and @name='v_codtdocide' and @id='v_codtdocide']", 
                            "//input[@type='text' and @name='v_codtra' and @id='v_codtra']", 
                            emp[CKEY_DOC_TYPE], emp[CKEY_DOC], enter=True)
    status, text = driver.accept_alert()
    if status:
        emp_registered_log(emp, bens, False, text)
        return

    driver.click_element("//input[@name='v_flgreing' and @value='N']")
    driver.click_element("//input[@name='v_flgcontseg' and @value='N']")

    date_value = auth[AUTH_SVL_CONSTANTS][AUTH_INS_DATE]
    if date_value is None:
        date_value = emp[CKEY_IDATE]
    if date_value is None:
        date_value = driver.attr_from_element("//input[@type='text' and @name='d_fecing']", 'value')
    if len(date_value) == 0:
        logging.warning('Can not find entry insurance date')
        driver.reload_page()
        emp_registered_log(emp, bens, False, OUT_CHK_REASONS['CFE'])
        return

    driver.write_in_element("//input[@type='text' and @name='d_fecasetra']", date_value)
    driver.write_in_element("//input[@type='text' and @name='n_monrem']", auth[AUTH_SVL_CONSTANTS][AUTH_SALARY])

    driver.click_element("//a[text()='Grabar']")

    reason = OUT_CHK_REASONS['OK']
    status, text = driver.accept_alert()
    if status:
        reason = text
    
    emp_registered_log(emp, bens, True, reason)

    return search_beneficier_by_doc(driver, auth, emp, bens)

def search_beneficier_by_doc(driver: w3auto.WebDriverExtended, auth, emp, bens):

    if employee_is_already_registered(driver,  emp[CKEY_DOC], emp[CKEY_DOC_TYPE]):
        driver.click_element("//a[img[@title='Ingresar Beneficiario(s)']]")
        driver.pick_window(1, 2)

        for index, ben in bens.iterrows():
            registered, reason = is_adult_question(driver, auth, emp, ben)
            ben_registered_log(emp, ben, registered, reason)

        return close_beneficier_page(driver, auth, emp, ben)

def is_adult_question(driver: w3auto.WebDriverExtended, auth, emp, ben) -> bool:

    if ben[CKEY_ISADULT]:
        return insert_just_doc(driver, auth, emp, ben)
    else:
        return insert_full_form(driver, auth, emp, ben)
    
def insert_just_doc(driver: w3auto.WebDriverExtended, auth, emp, ben) -> bool:
    
    driver.click_element("//input[@name='answer' and @value='no']")
    driver.send_doc_by_type("//select[@name='v_codtdocideben' and @id='v_codtdocideben']",
                            "//input[@type='text' and @name='v_codben' and @id='v_codben']",
                            ben[CKEY_DOC_TYPE], ben[CKEY_DOC], enter=True)
    status, text = driver.accept_alert()
    if status:#Data not found in MINTRA/RENIEC
        return False, text
    
    return save_beneficier_data(driver, auth, emp, ben)

def insert_full_form(driver: w3auto.WebDriverExtended, auth, emp, ben) -> bool:

    driver.click_element("//input[@name='answer' and @value='yes']")
    driver.send_doc_by_type("//select[@name='v_codtdocideben' and @id='v_codtdocideben']", 
                            "//input[@type='text' and @name='v_codben' and @name='v_codben']",
                            ben[CKEY_DOC_TYPE], ben[CKEY_DOC], enter=False)
    
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

def save_beneficier_data(driver: w3auto.WebDriverExtended, auth, emp, ben) -> bool:

    driver.select_in_element("//select[@name='n_codvinfam' and @class='form-control']", ben[CKEY_REL])

    driver.click_element("//a[text()='Grabar']")

    driver.accept_alert()

    return True, OUT_CHK_REASONS['OK']

def close_beneficier_page(driver: w3auto.WebDriverExtended, auth, emp, ben):
    
    driver.click_element("//a[text()='Regresar']")
    driver.pick_window(0, 1)

#EMPLOYEES TERMINATION

def terminate_employee(driver: w3auto.WebDriverExtended, auth, temp):

    if employee_is_already_registered(driver,  temp[CKEY_DOC], temp[CKEY_DOC_TYPE]):
        driver.click_element("//a[img[@title='Dar de Baja al Trabajador Asegurado']]")
        driver.pick_window(1, 2)

        driver.closest_match_from_element("//select[@name='tipomotivo' and @class='form-control']", temp[CKEY_REASON])
        driver.write_in_element("//input[@type='text' and @name='d_fecesttra' and @id='d_fecesttra']", temp[CKEY_TDATE]) 
        driver.click_element("//input[@type='checkbox' and @name='v_aceptabaja' and @value='on' and @id='v_aceptabaja']")
        driver.click_element("//a[text()='Grabar']")

        driver.accept_alert()
        terminated_log(temp, True, OUT_CHK_REASONS['OK'])

        driver.pick_window(0, 1)

        return
    
    terminated_log(temp, False, OUT_CHK_REASONS['EAT'])

def adjust_column_width(df, worksheet):
    for idx, col in enumerate(df):
        series = df[col]
        max_len = max((series.astype(str).map(len).max(), len(str(series.name))))
        worksheet.set_column(idx, idx, max_len + 2)

def run_svl(auth, csv_cache):
    if auth is not None:

        fdevinfo('STARTING WEBDRIVER ...')
        driver = w3auto.WebDriverExtended(auth[AUTH_WEBDRIVER][AUTH_BROWSER], 
                                        auth[AUTH_WEBDRIVER][AUTH_HEADLESS])
        fdevinfo('STARTING WEBDRIVER (OK)')
        fdevinfo('READING INPUT DATA ...')

        altas_dat, bajas_dat = False, False

        try:
            emps = pd.read_csv(csv_cache[0])
            bens = pd.read_csv(csv_cache[1])
            altas_dat = True
        except FileNotFoundError as e:
            fdevinfo('No input data for ALTAS')
        try:
            temps = pd.read_csv(csv_cache[2])
            bajas_dat = True
        except FileNotFoundError as e:
            fdevinfo('No input data for BAJAS')

        if altas_dat or bajas_dat:

            fdevinfo('READING INPUT DATA (OK)')

            fdevinfo('PROCESS: (ALTAS)')
            insurance_available = False
            try:
                insurance_available = from_login2update_revenue_insurance(driver, auth, emps, bens)
            except KeyboardInterrupt:
                driver.close_all()
                logging.info('Keyboard interrumption detected.')

            fdevinfo('PROCESS: (BAJAS)')
            try:
                insurance_available = from_login2update_revenue_insurance(driver, auth, temps, register_mode=False)
            except KeyboardInterrupt:
                driver.close_all()
                logging.info('Keyboard interrumption detected.')

            fdevinfo('WEBDRIVER SHUTDOWN')
            driver.quit()
            if insurance_available:
                fdevinfo('SAVING REPORT FILE ...')

                edf = pd.DataFrame(emp_registered_out[1:], columns=emp_registered_out[0]) 
                bdf = pd.DataFrame(ben_registered_out[1:], columns=ben_registered_out[0])
                tdf = pd.DataFrame(emp_terminated_out[1:], columns=emp_terminated_out[0])
                
                conf_file_out = auth[AUTH_NOTIFICATIONS][AUTH_FILEIO][AUTH_OUTPUT]
                
                if conf_file_out[AUTH_PARAM_USED]:
                    try:
                        output_file_path = conf_file_out[AUTH_FILE_PATH]
                        with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:
                            edf.to_excel(writer, sheet_name='Titulares asegurados', index=False)
                            bdf.to_excel(writer, sheet_name='Beneficiarios asegurados', index=False)
                            tdf.to_excel(writer, sheet_name='Titulares cesados', index=False)

                            # Adjust the column widths after all sheets have been written
                            adjust_column_width(edf, writer.sheets['Titulares asegurados'])
                            adjust_column_width(bdf, writer.sheets['Beneficiarios asegurados'])
                            adjust_column_width(tdf, writer.sheets['Titulares cesados'])

                        logging.info(f"REPORT FILE SAVED AT: {output_file_path}, SIZE: {os.path.getsize(output_file_path)} [bytes]")
                    except Exception as e:
                        errors.conserr(e, True)
                        logging.info(f"CAN NOT SAVE THE REPORT FILE. CHECK FOR ERRORS.")
                        
                        return False

                fdevinfo('SAVING REPORT FILE (OK)')
                fdevinfo('GOOD BYE!, SEE U NEXT TIME :)')

                conf_file_in = auth[AUTH_NOTIFICATIONS][AUTH_FILEIO][AUTH_INPUT]

                if os.path.isfile(conf_file_in[AUTH_FILE_PATH]):
                    os.remove(conf_file_in[AUTH_FILE_PATH])

        fdevinfo('GOOD BYE!, SEE U NEXT TIME :)')

        return True