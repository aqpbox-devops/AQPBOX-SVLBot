import pandas as pd
import json
import time
import argparse
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions

def load_json(file):

    try:
        with open(file, 'r', encoding='utf-8') as F:
            data = json.load(F)
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
    except TimeoutException:
        print("TLE: Page did not load in time")

def get_webdriver():

    try:
        driver_options = ChromeOptions()
        driver_options.add_argument("--start-maximized")
        driver = webdriver.Chrome(service=ChromeService(), options=driver_options)
    except WebDriverException:
        try:
            driver_options = EdgeOptions()
            driver_options.add_argument("--start-maximized")
            driver = webdriver.Edge(service=EdgeService(), options=driver_options)
        except WebDriverException:
            return None
    return driver

def verify_age(birth_date):

    age = (datetime.now() - birth_date).days // 365
    return age >= 18

def get_exdata(file, split_point):

    half_l, half_r = None, None
    
    try:
        df = pd.read_excel(file)
        half_l = df.iloc[:, :split_point]
        half_r = df.iloc[:, split_point:].copy()
        half_l = half_l.rename(columns={half_l.columns[-1]: 'EMP_DNI'})
        half_r[half_l.columns[-1]] = half_l.iloc[:, -1]
        half_r = half_r.rename(columns={half_r.columns[1]: 'BEN_DNI'})
        half_r = half_r.rename(columns={half_r.columns[0]: half_l.columns[0]})

        dni_columns_l = half_l.filter(like='DNI').columns
        half_l[dni_columns_l] = half_l[dni_columns_l].map(lambda x: str(x).zfill(8))

        dni_columns_r = half_r.filter(like='DNI').columns
        half_r[dni_columns_r] = half_r[dni_columns_r].map(lambda x: str(x).zfill(8))

        half_l = half_l.drop_duplicates()

        half_r['ADULT'] = half_r['FECHA DE NACIMIENTO'].apply(verify_age)

    except FileNotFoundError:
        print(f"FNF: File '{file}' not found.")

    return half_l, half_r

def login_employer_credentials(driver, auth_data):

    if driver is not None and auth_data is not None:

        print(driver)

        driver.get(auth_data['url'])

        driver.find_element(By.ID, 'txtRuc').send_keys(auth_data['ruc'])
        driver.find_element(By.ID, 'txtUsuario').send_keys(auth_data['user'])
        driver.find_element(By.ID, 'txtContrasena').send_keys(auth_data['psw'])
        driver.find_element(By.ID, 'btnAceptar').click()

        wait_page_loading(driver)

def update_renew_insurance(driver, auth_data, employee, beneficiers):

    employee_rlog = pd.DataFrame({'DNI': []})
    beneficier_rlog = pd.DataFrame({'DNI': []})

    def verify_beneficiaries(dni):
        """
        This function returns  True if the employee has been registered before.
        """
        driver.find_element(By.NAME, 'v_codtrabus').send_keys(dni)
        driver.execute_script('buscarTraLisBD();')

        wait_page_loading(driver)

        insurance_employee = driver.find_element(By.ID, 'lstPolizaTrabajador').find_element(By.TAG_NAME, 'tbody')
        if list(insurance_employee.find_elements(By.TAG_NAME, 'tr'))[0].get_attribute('class') != 'empty':
            print('worker exist')
            cell = driver.find_element(By.XPATH, '//a[img[@title="Ingresar Beneficiario(s)"]]')
            cell.click()
            return True
        return False
    
    def send_id_by_type(dni_column, ben=False, enter=True):
        """
        This function sends the document to RENIEC
        """
        (select_id, input_id) = ('v_codtdocide', 'v_codtra') if not ben else ('v_codtdocideben', 'v_codben')
        Select(driver.find_element(By.ID, select_id)).select_by_visible_text('DOCUMENTO NACIONAL DE IDENTIDAD')
        dni_input = driver.find_element(By.ID, input_id)
        dni_input.send_keys(dni_column)
        if not enter:
            return
        dni_input.send_keys(Keys.RETURN)

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

    if not verify_beneficiaries(employee['EMP_DNI']):

        wait_page_loading(driver)

        send_id_by_type(employee['EMP_DNI'])

        wait_page_loading(driver)

        driver.find_element(By.XPATH, "//input[@name='v_flgreing' and @value='N']").click()
        driver.find_element(By.XPATH, "//input[@name='v_flgcontseg' and @value='N']").click()
        if auth_data['insurance date'] is not None:
            date_value = auth_data['insurance date']
        else:
            date_value = driver.find_element(By.ID, 'd_fecing').get_attribute('value')
        if date_value == '':
            print('Can not find entry date')
            return
        driver.execute_script("arguments[0].setAttribute('value', arguments[1]);", driver.find_element(By.ID, 'd_fecasetra'), date_value)
        driver.find_element(By.NAME, 'n_monrem').send_keys(auth_data['const salary'])
        driver.execute_script('grabarPolizaxTra();')

        wait_page_loading(driver)

        verify_beneficiaries(employee['EMP_DNI'])#try again

    window_list = driver.window_handles
    assert(len(window_list) == 2)
    driver.switch_to.window(window_list[1])

    for index, beneficier in beneficiers.iterrows():
        wait_page_loading(driver)

        if not beneficier['ADULT']:

            time.sleep(0.25)
            
            driver.find_element(By.XPATH, "//input[@name='answer' and @value='yes']").click()

            time.sleep(0.25)

            send_id_by_type(beneficier['BEN_DNI'], ben=True, enter=False)
            driver.find_element(By.NAME, 'v_apepatben').send_keys(beneficier['APELLIDO PATERNO'])
            driver.find_element(By.NAME, 'v_apematben').send_keys(beneficier['APELLIDO MATERNO'])
            driver.find_element(By.NAME, 'v_nomben').send_keys(beneficier['NOMBRES'])
            date_value = beneficier['FECHA DE NACIMIENTO'].strftime("%d/%m/%Y")
            driver.execute_script("document.getElementById('d_fecnacben').value = arguments[0];", date_value)
            driver.find_element(By.NAME, 'v_direccion').send_keys(beneficier['DIRECCIÓN'])
            dept = beneficier['DEPARTAMENTO'].upper()
            prov = beneficier['PROVINCIA'].upper()
            dist = beneficier['DISTRITO'].upper()
            Select(driver.find_element(By.NAME, 'v_coddepBen')).select_by_visible_text(dept)
            time.sleep(0.15)
            Select(driver.find_element(By.NAME, 'v_codproBen')).select_by_visible_text(prov)
            time.sleep(0.15)
            Select(driver.find_element(By.NAME, 'v_coddisBen')).select_by_visible_text(dist)
            if beneficier['SEXO'].upper() == 'MASCULINO':
                driver.find_element(By.ID, 'v_gentraM').click()
            else:
                driver.find_element(By.ID, 'v_gentraF').click()
        
        else:
            send_id_by_type(beneficier['BEN_DNI'], ben=True)

        relationship = beneficier['VINCULO FAMILIAR'].upper()
        Select(driver.find_element(By.NAME, 'n_codvinfam')).select_by_visible_text(relationship)

        wait_page_loading(driver)
        
        driver.execute_script('grabarBeneficiario();')

        alert = driver.switch_to.alert
        alert.accept()

    driver.execute_script('regresar();')
    driver.switch_to.window(window_list[0]) 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seguro Vida Ley BotWeb.')
    parser.add_argument('auth_file', type=str, help='Path to the authentication JSON (RUC, Password, ...)')
    parser.add_argument('data_file', type=str, help='Path to the Excel file (Employees and beneficiers)')

    args = parser.parse_args()

    driver = get_webdriver()
    auth_data = load_json(args.auth_file)

    assert(auth_data is not None)
    employees_data, beneficiers_data = get_exdata(args.data_file, 2)

    print(employees_data.info(), beneficiers_data.info())
    print(employees_data.head(), beneficiers_data.head())

    login_employer_credentials(driver, auth_data)

    for index, employee in employees_data.iterrows():
        filtered_beneficiers = beneficiers_data.loc[beneficiers_data['EMP_DNI'] == employee['EMP_DNI']]
        print('Number of beneficiers: ', len(filtered_beneficiers))
        update_renew_insurance(driver, auth_data, employee, filtered_beneficiers)

    print('EVERYTHING WORKS OK')
    driver.quit()
