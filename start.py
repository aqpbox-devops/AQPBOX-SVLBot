import argparse
import subprocess

#python start.py '..\chrome\datos.xlsx' '..\chrome\auth_data.json'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seguro Vida Ley BotWeb.')
    parser.add_argument('data_file', type=str, help='Path to the Excel file (Employees and beneficiers)')
    parser.add_argument('auth_file', type=str, help='Path to the authentication JSON (RUC, Password, ...)')

    args = parser.parse_args()
    
    commands = [
        ['python', '(1) regs_preprocess.py', args.data_file],
        ['python', '(2) regs_automata.py', args.auth_file]
    ]

    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Comando '{' '.join(cmd)}' ejecutado exitosamente.")
            print("Salida del comando:", result.stdout)
        else:
            print(f"Error al ejecutar el comando '{' '.join(cmd)}'.")
            print("Salida del comando:", result.stdout)
            print("Error del comando:", result.stderr)
            break