#Shared registers, files
SHAREGS_PARSED_EMPLOYEES = 'SHARED-REGS/employees.csv'
SHAREGS_PARSED_BENEFICIERS = 'SHARED-REGS/beneficiers.csv'
SHAREGS_PARSED_TERMINATED = 'SHARED-REGS/terminated.csv'
SHAREGS_INFO_LOGS = 'SHARED-REGS/info-logs.log'
SHAREGS_WARNING_LOGS = 'SHARED-REGS/warn-logs.log'

SHAREGS_MATCH_LOG = 'SHARED-REGS/*.log'
SHAREGS_MATCH_CSV = 'SHARED-REGS/*.csv'

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
AUTH_SVL_CONSTANTS = 'svl'
AUTH_INS_DATE = 'insurance date'
AUTH_SALARY = 'insurance salary'
#Notifications
AUTH_NOTIFICATIONS = 'notifications'
AUTH_FILEIO = 'file io'

AUTH_INPUT = 'input'
AUTH_OUTPUT = 'output'
AUTH_PARAM_USED = 'active'
AUTH_FILE_PATH = 'path'

#Table columns names definitions
CKEY_ISADULT = 'ADULT'

LGENDER_VARS = ['M', 'MASCULINO']

CKEY_DOC = 'ID'
CKEY_DOC_TYPE = 'ID_T'
CKEY_PK = 'PK'

CKEY_IDATE = 'IDATE'
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

CKEY_REASON = 'WHY'
CKEY_TDATE = 'TDATE'

COLUMNS_ORD_AEMP = [CKEY_DOC_TYPE, CKEY_DOC, CKEY_IDATE]

COLUMNS_ORD_ABEN = [CKEY_DOC_TYPE, CKEY_DOC, CKEY_APPA, CKEY_APMA,
                   CKEY_NAME, CKEY_BDATE, CKEY_ADDR, CKEY_DEP, 
                   CKEY_PROV, CKEY_DIST, CKEY_SEX, CKEY_REL, CKEY_PK]

COLUMNS_ORD_CES = [CKEY_DOC_TYPE, CKEY_DOC, CKEY_REASON, CKEY_TDATE]
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

TERMINATION_REASONS = [
    "RENUNCIA",
    "RENUNCIA CON INCENTIVOS",
    "DESPIDO O DESTITUCION",
    "CESE COLECTIVO",
    "JUBILACIÓN",
    "INVALIDEZ ABSOLUTA PERMANENTE",
    "TERMINACION DE LA OBRA O SERVICIO, CUMPLIMIENTO CONDICIÓN RESOLUTORIA O VENCIMIENTO DEL PLAZO",
    "MUTUO DISENSO",
    "FALLECIMIENTO",
    "SUSPENSION DE LA PENSION",
    "REASIGNACIÓN SERVIDOR DE LA ADMINISTRACIÓN PÚBLICA",
    "PERMUTA SERVIDOR DE LA ADMINISTRACIÓN PÚBLICA",
    "TRANSFERENCIA SERVIDOR DE LA ADMINISTRACIÓN PÚBLICA",
    "BAJA POR SUCESIÓN EN POSICIÓN DEL EMPLEADOR",
    "EXTINCIÓN O LIQUIDACIÓN DEL EMPLEADOR",
    "OTROS MOTIVOS DE CADUCIDAD DE LA PENSIÓN",
    "NO SE INICIÓ LA RELACIÓN LABORAL O PRESTACIÓN EFECTIVA DE SERVICIOS",
    "LÍMITE DE EDAD 70 AÑOS",
    "OTRAS CAUSALES RÉGIMEN PÚBLICO GENERAL SERVICIO CIVIL - LEY 30057",
    "INHABILITACIÓN PARA EL EJERCICIO PROFESIONAL O DE LA FUNCIÓN PÚBLICA POR MÁS DE TRES MESES - LEY 30057",
    "SIN VÍNCULO LABORAL - HABILITADO PARA PDT PLAME"
]

#Output Registers vars
OUT_CHK_REASONS = {
    'OK': 'Se realizó correctamente.',
    'EAR': 'El trabajador ya fue registrado anteriormente.',
    'NFR': 'No se encontró los datos de la persona solicitada en RENIEC.',
    'BFI': 'Formato incorrecto de entrada del documento.',
    'CFE': 'No se muestra la fecha de inicio de la póliza para esta persona.',
    'EAT': 'El trabajador ya fue dado de baja anteriormente.'
}
