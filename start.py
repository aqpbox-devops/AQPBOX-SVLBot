import argparse, json
import scripts.bot.errors as errors
import scripts.template_gen as tgen
import scripts.input_formater as ifo
import scripts.svlauto as svlauto

from scripts.constants import *

def load_json(file):
    try:
        with open(file, 'r', encoding='utf-8') as F:
            data = json.load(F)
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        errors.conserr(e)
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seguro Vida Ley BotWeb.')
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-t', '--template', type=str, dest='auth_temp', help='Generate "auth" file template.')
    group.add_argument('-r', '--run', type=str, dest='auth_run', help='Execute the main process (The bot).')

    args = parser.parse_args()

    errors.setup_logging(SHAREGS_INFO_LOGS, SHAREGS_WARNING_LOGS)

    if args.auth_temp:
        tgen.generate_template(args.auth_temp)

    if args.auth_run:

        auth = load_json(args.auth_run)

        csv_cache = ifo.format_excel_input(auth)# READ DATA FROM FILE
        if svlauto.run_svl(auth, csv_cache):# EXECUTE BOT

            errors.clean_files(SHAREGS_MATCH_CSV)