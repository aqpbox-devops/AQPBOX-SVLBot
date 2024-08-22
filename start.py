import argparse
import subprocess

#python start.py 'test\input.xlsx' 'test\auth.json' 'test\out.xlsx'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seguro Vida Ley BotWeb.')
    parser.add_argument('in_file', type=str, help='Path to the Excel file (Employees and beneficiers)')
    parser.add_argument('auth_file', type=str, help='Path to the authentication JSON (RUC, Password, ...)')
    parser.add_argument('out_file', type=str, help='Path to the output file')

    args = parser.parse_args()
    
    commands = [
        ['python', 'scripts/bot_step1.py', args.in_file],
        ['python', 'scripts/bot_step2.py', args.auth_file],
        #['python', 'scripts/bot_step3.py', args.auth_file, args.out_file]
    ]

    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Comando '{' '.join(cmd)}' ejecutado exitosamente.")
            print("Salida del comando:", result.stdout)
        else:
            print(f"Error al ejecutar el comando '{' '.join(cmd)}'.")
            print("Error del comando:", result.stderr)
            break