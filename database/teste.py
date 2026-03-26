"""
Script para consultar e demonstrar operações na tabela de estações.
"""

import sys
import os
from pathlib import Path
from datetime import date
import sqlite3

# 1. Ajuste de Caminhos (garantindo que o Python encontre a pasta 'database')
diretorio_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if diretorio_projeto not in sys.path:
    sys.path.append(diretorio_projeto)

from database.repositories import EstacoesRepository
from database.db_manager import DatabaseManager


def exemplo_consultas():
    """Demonstra as operações do repositório de estações."""
    
    print("\n" + "="*70)
    print("CONSULTANDO E MANIPULANDO TABELA DE ESTAÇÕES")
    print("="*70)
    
    # Cria o repositório (que automaticamente inicializa o banco)
    print("\nInicializando repositório...")
    repo = EstacoesRepository()
    
    try:
        print("--- Conectando ao Banco de Dados ---")
        repo.conectar()
        print("✓ Conectado ao banco de dados\n")

        # OPERAÇÃO 1: Inserir estações
        print("--- OPERAÇÃO 1: Inserindo estações ---")
        try:
            repo.inserir(
                id_municipio='3106200',
                id_estacao='A701',
                estacao='Belo Horizonte',
                data_fundacao=date(2009, 1, 1),
                latitude=-19.9330,
                longitude=-43.9325,
                altitude=847.0
            )
            print("✓ Estação A701 inserida")
            
            repo.inserir(
                id_municipio='3144805',
                id_estacao='A703',
                estacao='Montes Claros',
                data_fundacao=date(2010, 1, 1),
                latitude=-16.7297,
                longitude=-43.8530,
                altitude=645.0
            )
            print("✓ Estação A703 inserida")
            
            repo.inserir(
                id_municipio='3144805',
                id_estacao='A705',
                estacao='Outro Site',
                data_fundacao=date(2011, 1, 1),
                latitude=-16.7500,
                longitude=-43.8500,
                altitude=650.0
            )
            print("✓ Estação A705 inserida\n")
            
        except sqlite3.IntegrityError:
            print("⚠ Algumas estações já existem (ignoradas)\n")
        except Exception as e:
            print(f"⚠ Erro ao inserir: {str(e)[:100]}\n")

        # OPERAÇÃO 2: Listar todas as estações
        print("--- OPERAÇÃO 2: Listando todas as estações cadastradas ---")
        estacoes = repo.listar_todas()
        
        if estacoes:
            print(f"{'ID Estação':<12} {'Nome':<25} {'Latitude':<12} {'Longitude':<12} {'Altitude':<10}")
            print("-" * 70)
            for est in estacoes:
                print(f"{est['id_estacao']:<12} {est['estacao']:<25} {est['latitude']:<12.4f} {est['longitude']:<12.4f} {est['altitude']:<10.1f}")
            print("-" * 70)
            print(f"Total de estações: {len(estacoes)}\n")
        else:
            print("Nenhuma estação encontrada!\n")

        # OPERAÇÃO 3: Buscar uma estação específica por ID
        print("--- OPERAÇÃO 3: Buscando estação específica (A701) ---")
        id_busca = "A701"
        estacao_unica = repo.obter_por_id(id_busca)
        
        if estacao_unica:
            print(f"Estação encontrada: {dict(estacao_unica)}\n")
        else:
            print(f"Estação {id_busca} não encontrada.\n")

        # OPERAÇÃO 4: Contagem total
        print("--- OPERAÇÃO 4: Contagem total ---")
        total = repo.contar()
        print(f"✓ Total de estações no banco: {total}\n")
        
        # OPERAÇÃO 5: Listar por município
        print("--- OPERAÇÃO 5: Filtrando por município (3144805) ---")
        estacoes_municipio = repo.listar_por_municipio('3144805')
        if estacoes_municipio:
            for est in estacoes_municipio:
                print(f"  • {est['id_estacao']}: {est['estacao']}")
            print()
        else:
            print("  Nenhuma estação encontrada para este município\n")
        
        # OPERAÇÃO 6: Atualizar dados
        print("--- OPERAÇÃO 6: Atualizando altitude de A701 ---")
        try:
            linhas = repo.atualizar('A701', altitude=850.0)
            if linhas > 0:
                estacao_atualizada = repo.obter_por_id('A701')
                print(f"✓ Altitude atualizada para: {estacao_atualizada['altitude']}m\n")
            else:
                print("⚠ Nenhuma estação atualizada\n")
        except Exception as e:
            print(f"⚠ Erro ao atualizar: {e}\n")

    except Exception as e:
        print(f"✗ Erro ao consultar: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        repo.desconectar()
        print("--- Conexão encerrada ---")
        print("="*70 + "\n")


if __name__ == "__main__":
    exemplo_consultas()