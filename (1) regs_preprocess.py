import pandas as pd
import argparse
from datetime import datetime
from __init__ import *

def verify_age(birth_date):

    age = (datetime.now() - birth_date).days // 365
    return age >= 18

def parse_as_nouns(text):
    words = text.split()
    
    capitalized_words = [word.title() for word in words]
    
    return ' '.join(capitalized_words)

def get_exdata(file):

    half_l, half_r = None, None
    split_point = 2
    
    try:
        df = pd.read_excel(file)
        half_l = df.iloc[:, :split_point]
        half_r = df.iloc[:, split_point:].copy()

        #col: EMPLOYEE DNI
        half_l = half_l.rename(columns={half_l.columns[1]: CKEY_DOC})
        #col: EMPLOYEE DNI copy in BENEFICIERS_TABLE (half_r)
        half_r[half_l.columns[1]] = half_l.iloc[:, 1]
        half_r = half_r.rename(columns={half_r.columns[-1]: CKEY_PK})
        #col: BENEFICIER DNI
        half_r = half_r.rename(columns={half_r.columns[1]: CKEY_DOC})
        #col: TIPO DE DOCUMENTO
        half_r = half_r.rename(columns={half_r.columns[0]: half_l.columns[0]})

        half_l.columns = COLUMNS_ORD[:2]
        half_r.columns = COLUMNS_ORD

        half_r[CKEY_DOC_TYPE] = half_r[CKEY_DOC_TYPE].str.replace(r'[^a-zA-Z]', '', regex=True)  # Eliminar todo lo que no sean letras
        half_r = half_r[half_r[CKEY_DOC_TYPE].str.strip() != '']

        half_r[CKEY_ISADULT] = half_r[CKEY_BDATE].apply(verify_age)
        half_r[CKEY_APPA] = half_r[CKEY_APPA].apply(parse_as_nouns)
        half_r[CKEY_APMA] = half_r[CKEY_APMA].apply(parse_as_nouns)
        half_r[CKEY_NAME] = half_r[CKEY_NAME].apply(parse_as_nouns)
        half_r[CKEY_BDATE] = half_r[CKEY_BDATE].dt.strftime("%d/%m/%Y").astype(str)
        half_r[CKEY_DEP] = half_r[CKEY_DEP].map(lambda x: x.upper())
        half_r[CKEY_PROV] = half_r[CKEY_PROV].map(lambda x: x.upper())
        half_r[CKEY_DIST] = half_r[CKEY_DIST].map(lambda x: x.upper())
        half_r[CKEY_SEX] = half_r[CKEY_SEX].fillna('undef')
        half_r[CKEY_SEX] = half_r[CKEY_SEX].map(lambda x: x.upper())

        half_r[CKEY_REL] = half_r[CKEY_REL].map(lambda x: RELATIONSHIPS[str(x)])

        half_l = half_l.drop_duplicates()
        half_r = half_r.drop_duplicates()

        half_l[CKEY_REGISTERED] = False
        half_r[CKEY_REGISTERED] = False

    except FileNotFoundError:
        print(f"FNF: File '{file}' not found.")

    return half_l, half_r

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seguro Vida Ley BotWeb.')
    parser.add_argument('data_file', type=str, help='Path to the Excel file (Employees and beneficiers)')

    args = parser.parse_args()

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    employees_data, beneficiers_data = get_exdata(args.data_file)

    employees_data.to_csv(SHAREGS_PARSED_EMPLOYEES, index=False)  
    beneficiers_data.to_csv(SHAREGS_PARSED_BENEFICIERS, index=False)