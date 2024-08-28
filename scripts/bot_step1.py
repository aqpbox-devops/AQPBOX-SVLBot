import pandas as pd
import argparse
import logging
from datetime import datetime

from constants import *
import bot.w3_automaton as w3auto

def verify_age(birth_date):

    age = (datetime.now() - birth_date).days // 365
    return age >= 18

def parse_as_nouns(text):
    words = text.split()
    
    capitalized_words = [word.title() for word in words]
    
    return ' '.join(capitalized_words)

def get_ex4register(df):

    split_point = 3
    
    emps = df.iloc[:, :split_point]
    bens = df.iloc[:, split_point:].copy()
    #col: EMPLOYEE DNI
    emps = emps.rename(columns={emps.columns[1]: CKEY_DOC})
    #col: EMPLOYEE DNI copy in BENEFICIERS_TABLE (bens)
    bens[emps.columns[1]] = emps.iloc[:, 1]
    bens = bens.rename(columns={bens.columns[-1]: CKEY_PK})
    #col: BENEFICIER DNI
    bens = bens.rename(columns={bens.columns[1]: CKEY_DOC})
    #col: TIPO DE DOCUMENTO
    bens = bens.rename(columns={bens.columns[0]: emps.columns[0]})

    emps.columns = COLUMNS_ORD_AEMP
    bens.columns = COLUMNS_ORD_ABEN

    bens[CKEY_DOC_TYPE] = bens[CKEY_DOC_TYPE].str.replace(r'[^a-zA-Z]', '', regex=True)  # Eliminar todo lo que no sean letras
    bens = bens[bens[CKEY_DOC_TYPE].str.strip() != '']

    bens[CKEY_ISADULT] = bens[CKEY_BDATE].apply(verify_age)
    bens[CKEY_APPA] = bens[CKEY_APPA].apply(parse_as_nouns)
    bens[CKEY_APMA] = bens[CKEY_APMA].apply(parse_as_nouns)
    bens[CKEY_NAME] = bens[CKEY_NAME].apply(parse_as_nouns)
    bens[CKEY_BDATE] = bens[CKEY_BDATE].dt.strftime("%d/%m/%Y").astype(str)
    bens[CKEY_DEP] = bens[CKEY_DEP].map(lambda x: x.upper())
    bens[CKEY_PROV] = bens[CKEY_PROV].map(lambda x: x.upper())
    bens[CKEY_DIST] = bens[CKEY_DIST].map(lambda x: x.upper())
    bens[CKEY_SEX] = bens[CKEY_SEX].fillna('undef')
    bens[CKEY_SEX] = bens[CKEY_SEX].map(lambda x: x.upper())

    bens[CKEY_REL] = bens[CKEY_REL].map(lambda x: RELATIONSHIPS[str(x)])

    emps[CKEY_IDATE] = emps[CKEY_IDATE].dt.strftime("%d/%m/%Y").astype(str)
    emps = emps.drop_duplicates()
    bens = bens.drop_duplicates()

    print(emps.info())
    print(bens.info())

    logging.info(f"To register: #Employees[{emps.shape[0]}], #Beneficiers[{bens.shape[0]}]")

    return emps, bens

def get_ex4terminated(df):
    cese = df
    cese.columns = COLUMNS_ORD_CES
    cese[CKEY_TDATE] = cese[CKEY_TDATE].dt.strftime("%d/%m/%Y").astype(str)
    cese[CKEY_REASON] = cese[CKEY_REASON].map(lambda x: x.upper())
    
    cese = cese.drop_duplicates()

    logging.info(f"To terminate: #Employees[{cese.shape[0]}]")

    return cese

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seguro Vida Ley BotWeb.')
    parser.add_argument('auth_file', type=str, help='Path to the authentication JSON (RUC, Password, ...)')

    args = parser.parse_args()

    auth = w3auto.load_json(args.auth_file)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    w3auto.setup_logging(SHAREGS_INFO_LOGS, SHAREGS_WARNING_LOGS)
    
    conf_file_in = auth[AUTH_NOTIFICATIONS][AUTH_FILEIO][AUTH_INPUT]
    
    if conf_file_in[AUTH_PARAM_USED]: 

        try:

            file_content = pd.read_excel(conf_file_in[AUTH_FILE_PATH], sheet_name=None)
        
        except FileNotFoundError as e:
            w3auto.conserr(e)

        df_to_insert = file_content['Ingresos']
        df_to_delete = file_content['Ceses']

        remps, rbens = get_ex4register(df_to_insert)

        temps = get_ex4terminated(df_to_delete)

        remps.to_csv(SHAREGS_PARSED_EMPLOYEES, index=False)  
        rbens.to_csv(SHAREGS_PARSED_BENEFICIERS, index=False)
        temps.to_csv(SHAREGS_PARSED_TERMINATED, index=False)