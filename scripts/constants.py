#Shared registers, files
SHAREGS_PARSED_EMPLOYEES = 'SHARED-REGS/employees.csv'
SHAREGS_PARSED_BENEFICIERS = 'SHARED-REGS/beneficiers.csv'
SHAREGS_INFO_LOGS = 'SHARED-REGS/info-logs.log'
SHAREGS_WARNING_LOGS = 'SHARED-REGS/warn-logs.log'

#JSON Authentication file keys
AUTH_URL = 'url'
AUTH_WEBDRIVER = 'webdriver'
AUTH_BROWSER = 'browser'
AUTH_HEADLESS = 'headless'
#Credentials
AUTH_CREDENTIALS = 'login'
AUTH_USER = 'user'
AUTH_PASSWORD = 'password'
AUTH_RUC = 'ruc'
#Inside the page
AUTH_SVL_CONSTANTS = 'SVL'
AUTH_INS_DATE = 'insurance date'
AUTH_SALARY = 'insurance salary'
#Notifications
AUTH_NOTIFICATIONS = 'notifications'
AUTH_SENDER = 'sender login'
AUTH_EMAIL = 'email'
AUTH_SMTP = 'server smtp'
AUTH_SUBSCRIBER_LIST = 'subscribers'

#Table columns names definitions
CKEY_REGISTERED = 'REGISTERED'
CKEY_ISADULT = 'ADULT'

LGENDER_VARS = ['M', 'MASCULINO']

CKEY_DOC = 'ID'
CKEY_DOC_TYPE = 'ID_T'
CKEY_PK = 'PK'

CKEY_APPA = 'APPA'
CKEY_APMA = 'APMA'
CKEY_NAME = 'NAME'
CKEY_BDATE = 'BDATE'
CKEY_ADDR = 'ADDR'
CKEY_DEP = 'DEP'
CKEY_PROV = 'PROV'
CKEY_DIST = 'DIST'
CKEY_SEX = 'SEX'
CKEY_REL = 'REL'

COLUMNS_ORD = [CKEY_DOC_TYPE, CKEY_DOC, CKEY_APPA, CKEY_APMA,
               CKEY_NAME, CKEY_BDATE, CKEY_ADDR, CKEY_DEP, 
               CKEY_PROV, CKEY_DIST, CKEY_SEX, CKEY_REL, CKEY_PK]

#SVL definitions
ID_DOC_TYPES = {
    'DNI': {'full name': 'DOCUMENTO NACIONAL DE IDENTIDAD', 'len': 8},
    'CEX': {'full name': 'CARNÉ DE EXTRANJERÍA', 'len': 9},
    'PP': {'full name': 'PASAPORTE', 'len': 8},
    'CSRF': {'full name': 'CARNET DE SOLICITUD DE REFUGIO', 'len': 9},
    'PTP': {'full name': 'PERMISO TEMPORAL DE PERMANENCIA', 'len': 15},
    'CPTP': {'full name': 'CARNÉ DE PERMISO TEMPORAL DE PERMANENCIA', 'len': 8}
}
RELATIONSHIPS = {
    "69": "HIJO (A)",
    "66": "CONYUGE",
    "91": "CONCUBINA(O)",
    "71": "PADRE/MADRE",
    "a": "HERMANOS MENORES DE 18 AÑOS",
    "b": "NIETO/NIETA",
    "c": "ABUELO/ABUELA",
    "d": "ESPOSO (A)",
    "e": "BISNIETO (A)",
    "f": "TATARANIETO (A)",
    "g": "BISABUELO (A)",
    "h": "TATARABUELO (A)",
    "i": "SOBRINO (A)",
    "j": "TÍO (A)"
}
