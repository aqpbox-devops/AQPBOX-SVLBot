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

def get_exdata(file):

    emps, bens = None, None
    split_point = 2
    
    try:
        df = pd.read_excel(file)
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

        emps.columns = COLUMNS_ORD[:split_point]
        bens.columns = COLUMNS_ORD

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

        emps = emps.drop_duplicates()
        bens = bens.drop_duplicates()

        emps[CKEY_REGISTERED] = False
        bens[CKEY_REGISTERED] = False

        logging.info(f"{emps.shape}{bens.shape}")

    except FileNotFoundError as e:
        w3auto.conserr(e)

    return emps, bens

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seguro Vida Ley BotWeb.')
    parser.add_argument('data_file', type=str, help='Path to the Excel file (Employees and beneficiers)')

    args = parser.parse_args()

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    w3auto.setup_logging(SHAREGS_INFO_LOGS, SHAREGS_WARNING_LOGS)

    emps, bens = get_exdata(args.data_file)

    try:
        if bens is None or emps is None:
            raise ValueError("The generation of DataFrames 'bens' and 'emps' failed. Both are null.")

    except Exception as e:
        w3auto.conserr(e)

    emps.to_csv(SHAREGS_PARSED_EMPLOYEES, index=False)  
    bens.to_csv(SHAREGS_PARSED_BENEFICIERS, index=False)