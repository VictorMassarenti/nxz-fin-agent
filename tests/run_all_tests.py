#!/usr/bin/env python3
"""
Runner de testes para executar todos os testes do projeto
"""

import sys
import os
import subprocess

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_test_file(filename):
    """Executa um arquivo de teste específico"""
    print(f"Executando {filename}...")
    try:
        result = subprocess.run([
            sys.executable, '-m', f'tests.{filename.replace(".py", "")}'
        ], cwd=os.path.join(os.path.dirname(__file__), '..'), 
           capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✓ {filename} executado com sucesso")
            print(result.stdout)
        else:
            print(f"✗ {filename} falhou")
            print(result.stderr)
        print()
    except subprocess.TimeoutExpired:
        print(f"✗ {filename} excedeu o tempo limite")
        print()
    except Exception as e:
        print(f"✗ Erro ao executar {filename}: {e}")
        print()

def main():
    """Executa todos os testes do projeto"""
    print("Executando todos os testes do projeto...\n")
    
    # Listar todos os arquivos de teste
    test_files = [f for f in os.listdir(os.path.dirname(__file__)) if f.startswith('test_') and f.endswith('.py')]
    
    # Executar cada arquivo de teste
    for test_file in test_files:
        run_test_file(test_file)
    
    print("Execução de todos os testes concluída.")

if __name__ == "__main__":
    main()