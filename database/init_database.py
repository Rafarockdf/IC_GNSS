import sqlite3
import os
from pathlib import Path

def criar_banco_dados(caminho_banco: str = None):
    """
    Cria um banco de dados SQLite e executa o DDL para criar as tabelas.
    
    Args:
        caminho_banco (str): Caminho para o banco de dados. 
                            Se None, cria na pasta database com nome 'gnss.db'
    """
    
    # Define o caminho do banco de dados
    if caminho_banco is None:
        diretorio_atual = Path(__file__).parent
        caminho_banco = str(diretorio_atual / 'gnss.db')
    
    # Define o caminho do arquivo DDL.sql
    diretorio_atual = Path(__file__).parent
    caminho_ddl = str(diretorio_atual / 'DDL.sql')
    
    # Verifica se o arquivo DDL.sql existe
    if not os.path.exists(caminho_ddl):
        raise FileNotFoundError(f"Arquivo DDL.sql não encontrado em: {caminho_ddl}")
    
    try:
        # Conecta ao banco de dados (cria se não existir)
        conexao = sqlite3.connect(caminho_banco)
        cursor = conexao.cursor()
        
        print(f"✓ Banco de dados criado/conectado em: {caminho_banco}")
        
        # Lê o arquivo DDL.sql
        with open(caminho_ddl, 'r', encoding='utf-8') as arquivo:
            script_ddl = arquivo.read()
        
        # Executa o script DDL
        cursor.executescript(script_ddl)
        
        # Commit das mudanças
        conexao.commit()
        
        print("✓ Tabelas criadas com sucesso!")
        
        # Lista as tabelas criadas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        
        print("\nTabelas criadas:")
        for tabela in tabelas:
            print(f"  - {tabela[0]}")
        
        # Lista os índices criados
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indices = cursor.fetchall()
        
        if indices:
            print("\nÍndices criados:")
            for indice in indices:
                print(f"  - {indice[0]}")
        
        conexao.close()
        print("\n✓ Operação concluída com sucesso!")
        
        return caminho_banco
        
    except sqlite3.Error as e:
        print(f"✗ Erro ao criar banco de dados: {e}")
        raise
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")
        raise


if __name__ == "__main__":
    # Executa a criação do banco de dados
    caminho = criar_banco_dados()
