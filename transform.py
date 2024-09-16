import json
import os
import pandas as pd
from typing import List, Dict

CONFIG_FILE = 'configs.json'
OUTPUT_FOLDER = 'output'

def load_configs() -> Dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_configs(configs: Dict):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(configs, f, indent=2)

def create_config() -> Dict:
    print("\nCreando nueva configuración:")
    name = input("Nombre de la configuración: ")
    row_delimiter = input("Delimitador de filas: ")
    col_delimiter = input("Delimitador de columnas: ")
    num_columns = int(input("Número de columnas: "))
    column_names = [input(f"Nombre de la columna {i+1}: ") for i in range(num_columns)]
    
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
            print(f"Advertencia: Fila ignorada debido a número incorrecto de columnas: {row}")
    
    return pd.DataFrame(processed_rows, columns=config['column_names'])

def export_to_csv(df: pd.DataFrame, config_name: str):
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    
    filename = f"{OUTPUT_FOLDER}/{config_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"\nDatos exportados a: {filename}")

def select_config(configs: Dict) -> Dict:
    while True:
        print("\nConfiguraciones disponibles:")
        for i, (name, config) in enumerate(configs.items(), 1):
            print(f"{i}. {name}")
        print("0. Crear nueva configuración")
        
        choice = input("Seleccione una configuración (0-4): ")
        if choice == '0':
            if len(configs) >= 4:
                print("Ya existen 4 configuraciones. Elimine una antes de crear una nueva.")
            else:
                new_config = create_config()
                configs[new_config['name']] = new_config
                save_configs(configs)
                return new_config
        elif choice.isdigit() and 1 <= int(choice) <= len(configs):
            return list(configs.values())[int(choice) - 1]
        else:
            print("Opción no válida. Intente de nuevo.")

def process_continuous(config: Dict):
    print(f"\nUsando configuración: {config['name']}")
    print("Pegue los datos a procesar (presione Enter dos veces para finalizar, o escriba 'salir' para volver al menú principal):")
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
        print("\nListo para procesar más datos. Pegue los nuevos datos o escriba 'salir' para volver al menú principal:")

def main():
    configs = load_configs()
    
    while True:
        print("\n--- Procesador de Datos ---")
        print("1. Seleccionar configuración y procesar datos")
        print("2. Gestionar configuraciones")
        print("3. Salir")
        
        choice = input("Seleccione una opción: ")
        
        if choice == '1':
            if not configs:
                print("No hay configuraciones guardadas. Cree una primero.")
                new_config = create_config()
                configs[new_config['name']] = new_config
                save_configs(configs)
                config = new_config
            else:
                config = select_config(configs)
            process_continuous(config)
        
        elif choice == '2':
            config = select_config(configs)
            print(f"\nConfiguración seleccionada: {config['name']}")
            print(json.dumps(config, indent=2))
            if input("¿Desea eliminar esta configuración? (s/n): ").lower() == 's':
                del configs[config['name']]
                save_configs(configs)
                print("Configuración eliminada.")
        
        elif choice == '3':
            print("¡Hasta luego!")
            break
        
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()