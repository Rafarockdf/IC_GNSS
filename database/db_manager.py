"""
Módulo de gerenciamento do banco de dados.
Centraliza a lógica de criação e inicialização.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional


class DatabaseManager:
    """Gerencia a criação e inicialização do banco de dados SQLite."""
    
    _banco_inicializado = False
    _caminho_banco = None
    
    @classmethod
    def obter_caminho_banco(cls, caminho_banco: Optional[str] = None) -> str:
        """
        Obtém o caminho do banco de dados.
        
        Args:
            caminho_banco (str): Caminho customizado, se fornecido
            
        Returns:
            str: Caminho completo para o banco
        """
        if caminho_banco:
            return caminho_banco
        
        if cls._caminho_banco:
            return cls._caminho_banco
        
        # Caminho padrão: pasta 'database' com arquivo gnss.db
        diretorio_database = Path(__file__).parent
        cls._caminho_banco = str(diretorio_database / 'gnss.db')
        return cls._caminho_banco
    
    @classmethod
    def inicializar_banco(cls, caminho_banco: Optional[str] = None, forcar: bool = False) -> str:
        """
        Inicializa o banco de dados criando ele e suas tabelas se necessário.
        
        Args:
            caminho_banco (str): Caminho customizado para o banco
            forcar (bool): Se True, recria o banco mesmo que já exista
            
        Returns:
            str: Caminho do banco de dados criado/inicializado
        """
        if cls._banco_inicializado and not forcar:
            return cls.obter_caminho_banco(caminho_banco)
        
        caminho = cls.obter_caminho_banco(caminho_banco)
        diretorio_database = Path(__file__).parent
        caminho_ddl = str(diretorio_database / 'DDL.sql')
        
        # Verifica se o arquivo DDL.sql existe
        if not os.path.exists(caminho_ddl):
            raise FileNotFoundError(
                f"Arquivo DDL.sql não encontrado em: {caminho_ddl}\n"
                "Certifique-se de que o arquivo existe no diretório 'database/"
            )
        
        try:
            # Remove banco existente se forcar=True
            if forcar and os.path.exists(caminho):
                os.remove(caminho)
                print(f"✓ Banco de dados anterior removido: {caminho}")
            
            # Conecta ao banco (cria se não existir)
            conexao = sqlite3.connect(caminho)
            cursor = conexao.cursor()
            
            print(f"✓ Banco de dados criado/conectado em: {caminho}")
            
            # Lê o arquivo DDL.sql
            with open(caminho_ddl, 'r', encoding='utf-8') as arquivo:
                script_ddl = arquivo.read()
            
            # Executa o script DDL
            cursor.executescript(script_ddl)
            conexao.commit()
            
            print("✓ Tabelas criadas com sucesso!")
            
            # Lista as tabelas criadas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tabelas = cursor.fetchall()
            
            print("  Tabelas:")
            for tabela in tabelas:
                print(f"    - {tabela[0]}")
            
            # Lista os índices criados
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
            indices = cursor.fetchall()
            
            if indices:
                print("  Índices:")
                for indice in indices:
                    if not indice[0].startswith('sqlite_'):
                        print(f"    - {indice[0]}")
            
            conexao.close()
            
            cls._banco_inicializado = True
            print("✓ Banco de dados inicializado com sucesso!\n")
            
            return caminho
            
        except sqlite3.Error as e:
            print(f"✗ Erro SQLite ao criar banco: {e}")
            raise
        except Exception as e:
            print(f"✗ Erro inesperado na inicialização: {e}")
            raise
    
    @classmethod
    def banco_existe(cls, caminho_banco: Optional[str] = None) -> bool:
        """
        Verifica se o banco de dados existe.
        
        Args:
            caminho_banco (str): Caminho customizado
            
        Returns:
            bool: True se existe, False caso contrário
        """
        caminho = cls.obter_caminho_banco(caminho_banco)
        return os.path.exists(caminho)
    
    @classmethod
    def resetar_cache(cls):
        """Reseta o cache de inicialização (útil para testes)."""
        cls._banco_inicializado = False
        cls._caminho_banco = None
