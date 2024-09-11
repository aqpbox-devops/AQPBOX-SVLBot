import json
from scripts.constants import *

data = {
    AUTH_URL: "https://api-seguridad.sunat.gob.pe/v1/clientessol/b3639111-1546-4d06-b74f-de2c40629748/oauth2/login?originalUrl=https://apps.trabajo.gob.pe/si.segurovida/index.jsp&state=m1ntr4",
    AUTH_WEBDRIVER: {
        AUTH_BROWSER: "(edge, chrome, firefox, safari)",
        AUTH_HEADLESS: "(true, false)"
    },
    AUTH_CREDENTIALS: {
        AUTH_RUC: "xxxxxxxxxxx",
        AUTH_USER: "xxxxxxxx",
        AUTH_PASSWORD: "xxxxxxxx"
    },
    AUTH_SVL_CONSTANTS: {
        AUTH_INS_DATE: "(None, 'dd/mm/Y')",
        AUTH_SALARY: "(Number: INT)"
    },
    AUTH_NOTIFICATIONS: {
        AUTH_FILEIO: {
            AUTH_INPUT: {
                AUTH_PARAM_USED: "(true, false)",
                AUTH_FILE_PATH: "PATH/TO/input.xlsx"
            },
            AUTH_OUTPUT: {
                AUTH_PARAM_USED: "(true, false)",
                AUTH_FILE_PATH: "PATH/TO/output.xlsx"
            }
        }
    }
}

def generate_template(fn_template: str):
     with open(fn_template, "w") as file:
        json.dump(data, file, indent=4)