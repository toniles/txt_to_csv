import json
import os
import pandas as pd
from typing import List, Dict
from colorama import init, Fore, Back, Style

# Inicializar colorama
init(autoreset=True)

CONFIG_FILE = 'configs.json'
OUTPUT_FOLDER = 'output'

ASCII_LOGO = """
 ██████ ██      ██ ██████  ██████   ██████   █████  ██████  ██████          ██   ██   ██                ██████ ███████ ██    ██     
██      ██      ██ ██   ██ ██   ██ ██    ██ ██   ██ ██   ██ ██   ██          ██   ██   ██              ██      ██      ██    ██     
██      ██      ██ ██████  ██████  ██    ██ ███████ ██████  ██   ██           ██   ██   ██             ██      ███████ ██    ██     
██      ██      ██ ██      ██   ██ ██    ██ ██   ██ ██   ██ ██   ██          ██   ██   ██              ██           ██  ██  ██      
 ██████ ███████ ██ ██      ██████   ██████  ██   ██ ██   ██ ██████          ██   ██   ██                ██████ ███████   ████       
                                                                                                                                                                                                                                                                                                 
"""

def print_ascii_logo():
    print(Fore.CYAN + ASCII_LOGO)
    print(Style.RESET_ALL)

def load_configs() -> Dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_configs(configs: Dict):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(configs, f, indent=2)

def create_config() -> Dict:
    print(Fore.YELLOW + "\nCreando nueva configuración:")
    name = input(Fore.GREEN + "Nombre de la configuración: " + Style.RESET_ALL)
    row_delimiter = input(Fore.GREEN + "Delimitador de filas: " + Style.RESET_ALL)
    col_delimiter = input(Fore.GREEN + "Delimitador de columnas: " + Style.RESET_ALL)
    num_columns = int(input(Fore.GREEN + "Número de columnas: " + Style.RESET_ALL))
    column_names = [input(Fore.GREEN + f"Nombre de la columna {i+1}: " + Style.RESET_ALL) for i in range(num_columns)]
    
    return {
        "name": name,
        "row_delimiter": row_delimiter,
        "col_delimiter": col_delimiter,
        "num_columns": num_columns,
        "column_names": column_names
    }

def process_data(data: str, config: Dict) -> pd.DataFrame:
    rows = data.split(config['row_delimiter'])
    processed_rows = []
    for row in rows:
        cols = row.split(config['col_delimiter'])
        if len(cols) == config['num_columns']:
            processed_rows.append(cols)
        else:
            print(Fore.RED + f"Advertencia: Fila ignorada debido a número incorrecto de columnas: {row}" + Style.RESET_ALL)
    
    return pd.DataFrame(processed_rows, columns=config['column_names'])

def export_to_csv(df: pd.DataFrame, config_name: str):
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    filename = f"{OUTPUT_FOLDER}/{config_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(Fore.GREEN + f"\nDatos exportados a: {filename}" + Style.RESET_ALL)

def select_config(configs: Dict) -> Dict:
    while True:
        print(Fore.YELLOW + "\nConfiguraciones disponibles:")
        for i, (name, config) in enumerate(configs.items(), 1):
            print(Fore.CYAN + f"{i}. {name}")
        print(Fore.MAGENTA + "0. Crear nueva configuración")
        
        choice = input(Fore.GREEN + "Seleccione una configuración (0-4): " + Style.RESET_ALL)
        if choice == '0':
            if len(configs) >= 4:
                print(Fore.RED + "Ya existen 4 configuraciones. Elimine una antes de crear una nueva." + Style.RESET_ALL)
            else:
                new_config = create_config()
                configs[new_config['name']] = new_config
                save_configs(configs)
                return new_config
        elif choice.isdigit() and 1 <= int(choice) <= len(configs):
            return list(configs.values())[int(choice) - 1]
        else:
            print(Fore.RED + "Opción no válida. Intente de nuevo." + Style.RESET_ALL)

def process_continuous(config: Dict):
    print(Fore.YELLOW + f"\nUsando configuración: {config['name']}")
    print(Fore.CYAN + "Pegue los datos a procesar (presione Enter dos veces para finalizar, o escriba 'salir' para volver al menú principal):")
    while True:
        lines = []
        while True:
            line = input()
            if line.lower() == 'salir':
                return
            if line:
                lines.append(line)
            else:
                break
        
        if not lines:
            continue
        
        data = '\n'.join(lines)
        df = process_data(data, config)
        export_to_csv(df, config['name'])
        print(Fore.GREEN + "\nDatos procesados con éxito." + Style.RESET_ALL)
        print(Fore.CYAN + "Listo para procesar más datos. Pegue los nuevos datos o escriba 'salir' para volver al menú principal:")

def main():
    configs = load_configs()
    
    while True:
        print_ascii_logo()
        print(Fore.YELLOW + "--- Procesa cualquier texto con doble delimitador a CSV ---")
        print(Fore.CYAN + "1. Seleccionar configuración y procesar datos")
        print(Fore.CYAN + "2. Gestionar configuraciones")
        print(Fore.CYAN + "3. Salir")
        
        choice = input(Fore.GREEN + "Seleccione una opción: " + Style.RESET_ALL)
        
        if choice == '1':
            if not configs:
                print(Fore.YELLOW + "No hay configuraciones guardadas. Cree una primero.")
                new_config = create_config()
                configs[new_config['name']] = new_config
                save_configs(configs)
                config = new_config
            else:
                config = select_config(configs)
            process_continuous(config)
        
        elif choice == '2':
            config = select_config(configs)
            print(Fore.YELLOW + f"\nConfiguración seleccionada: {config['name']}")
            print(Fore.CYAN + json.dumps(config, indent=2))
            if input(Fore.MAGENTA + "¿Desea eliminar esta configuración? (s/n): " + Style.RESET_ALL).lower() == 's':
                del configs[config['name']]
                save_configs(configs)
                print(Fore.GREEN + "Configuración eliminada.")
        
        elif choice == '3':
            print(Fore.YELLOW + "¡Hasta luego!" + Style.RESET_ALL)
            break
        
        else:
            print(Fore.RED + "Opción no válida. Intente de nuevo." + Style.RESET_ALL)

if __name__ == "__main__":
    main()