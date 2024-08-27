import argparse
import subprocess
import glob
import json
from scripts.constants import *

def clean_files(file_like):
    for fp in glob.glob(file_like):
        with open(fp, 'w') as f:
            pass

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seguro Vida Ley BotWeb.')
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-t', '--template', type=str, dest='auth_temp', help='Generate "auth" file template.')
    group.add_argument('-r', '--run', type=str, dest='auth_run', help='Execute the main process (The bot).')

    args = parser.parse_args()

    if args.auth_temp:
        with open(args.auth_temp, "w") as file:
            json.dump(data, file, indent=4)

    if args.auth_run:
        clean_files('SHARED-REGS/*.log')
        
        commands = [
            ['python', 'scripts/bot_step1.py', args.auth_run],
            ['python', 'scripts/bot_step2.py', args.auth_run],
        ]

        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("SUCCESS:", result.stdout)
            else:
                print("ERROR:", result.stderr)
                break