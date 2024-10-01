import pandas as pd
import logging, os, glob
from datetime import datetime

from scripts.constants import *
import scripts.bot.errors as errors
import hashlib

def hash_excel(file_content):
    combined_string = ""
    for sheet_name, df in file_content.items():
        combined_string += df.to_string(index=False)
    
    combined_bytes = combined_string.encode('utf-8')
    return hashlib.sha256(combined_bytes).hexdigest()

def verify_hash_in_files(end_file_csv: str, file_paths):
    all_exist = True
    all_match = True

    for path in file_paths:
        if not os.path.exists(path):
            print(f"File does not exist: {path}")
            all_exist = False
            all_match = False  # Si uno no existe, no puede coincidir

        else:
            all_match = all_match and str(path).endswith(end_file_csv)

    return all_exist and all_match

def verify_age(birth_date):

    age = (datetime.now() - birth_date).days // 365
    return age >= 18

def parse_as_nouns(text):
    words = str(text).split()
    
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
    bens[CKEY_DEP] = bens[CKEY_DEP].map(lambda x: str(x).upper())
    bens[CKEY_PROV] = bens[CKEY_PROV].map(lambda x: str(x).upper())
    bens[CKEY_DIST] = bens[CKEY_DIST].map(lambda x: str(x).upper())
    bens[CKEY_SEX] = bens[CKEY_SEX].fillna('undef')
    bens[CKEY_SEX] = bens[CKEY_SEX].map(lambda x: str(x).upper())
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

    print(cese.info())

    logging.info(f"To terminate: #Employees[{cese.shape[0]}]")

    return cese

def check_file(auth_file_path):
    if not os.path.isfile(auth_file_path):
        directory = os.path.dirname(auth_file_path)
        new_files = glob.glob(os.path.join(directory, '*.xlsx'))
        if new_files:
            auth_file_path = new_files[0]
    return auth_file_path

def format_excel_input(auth):

    conf_file_in = auth[AUTH_NOTIFICATIONS][AUTH_FILEIO][AUTH_INPUT]
    
    if conf_file_in[AUTH_PARAM_USED]: 

        conf_file_in[AUTH_FILE_PATH] = check_file(conf_file_in[AUTH_FILE_PATH])
        logging.info(f"Input file is: {conf_file_in[AUTH_FILE_PATH]}")

        hash_code = '0'
        
        try:
            file_content = pd.read_excel(conf_file_in[AUTH_FILE_PATH], sheet_name=None)

            hash_code = hash_excel(file_content)
            
        except FileNotFoundError as e:
            errors.conserr(e)

        end_file_csv = f"_{hash_code}.csv"

        csv_f = (SHAREGS_PARSED_EMPLOYEES + end_file_csv,
                 SHAREGS_PARSED_BENEFICIERS + end_file_csv, 
                 SHAREGS_PARSED_TERMINATED + end_file_csv)

        if verify_hash_in_files(end_file_csv, [SHAREGS_PARSED_EMPLOYEES, 
                                            SHAREGS_PARSED_BENEFICIERS, 
                                            SHAREGS_PARSED_TERMINATED]):
            return csv_f

        try:

            df_to_insert = file_content['Ingresos']
            df_to_delete = file_content['Ceses']

            remps, rbens = get_ex4register(df_to_insert)

            temps = get_ex4terminated(df_to_delete)

        except (ValueError, TypeError, KeyError) as e:
            logging.warning("The input excel file does not match the required format.")
            errors.conserr(e)

        errors.clean_files(SHAREGS_MATCH_LOG)
        errors.clean_files(SHAREGS_MATCH_CSV)

        remps.to_csv(csv_f[0], index=False)  
        rbens.to_csv(csv_f[1], index=False)
        temps.to_csv(csv_f[2], index=False)

        return csv_f

        #if os.path.isfile(conf_file_in[AUTH_FILE_PATH]):
        #    os.remove(conf_file_in[AUTH_FILE_PATH])