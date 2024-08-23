import argparse
import subprocess
import glob

def clean_files(file_like):
    for fp in glob.glob(file_like):
        with open(fp, 'w') as f:
            pass

#python start.py 'test\auth.json'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seguro Vida Ley BotWeb.')
    parser.add_argument('auth_file', type=str, help='Path to the authentication JSON (RUC, Password, ...)')

    args = parser.parse_args()

    clean_files('SHARED-REGS/*.log')
    
    commands = [
        ['python', 'scripts/bot_step1.py', args.auth_file],
        ['python', 'scripts/bot_step2.py', args.auth_file],
    ]

    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("SUCCESS:", result.stdout)
        else:
            print("ERROR:", result.stderr)
            break