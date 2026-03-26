import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from database.db_manager import DatabaseManager


class BaseRepository(ABC):
    def __init__(self, caminho_banco: str = None):
        """
        Inicializa o repositório.
        
        Args:
            caminho_banco (str): Caminho customizado para o banco
        """
        # Garante que o banco foi inicializado
        self.caminho_banco = DatabaseManager.inicializar_banco(caminho_banco)
        self.conexao = None
    
    def conectar(self):
        """Abre a conexão com o banco de dados."""
        if not self.conexao:
            self.conexao = sqlite3.connect(self.caminho_banco)
            self.conexao.row_factory = sqlite3.Row
        return self.conexao
    
    def desconectar(self):
        """Fecha a conexão com o banco de dados."""
        if self.conexao:
            self.conexao.close()
    
    def _obter_cursor(self):
        """Retorna um cursor da conexão atual."""
        if self.conexao is None:
            self.conectar()
        return self.conexao.cursor()
    
    def executar(self, sql: str, parametros: tuple = None) -> int:
        """
        Executa uma query de modificação (INSERT, UPDATE, DELETE).
        
        Args:
            sql (str): Query SQL
            parametros (tuple): Parâmetros da query
            
        Returns:
            int: ID da última linha inserida ou linhas afetadas
        """
        cursor = self._obter_cursor()
        try:
            if parametros:
                cursor.execute(sql, parametros)
            else:
                cursor.execute(sql)
            self.conexao.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            self.conexao.rollback()
            raise Exception(f"Erro ao executar query: {e}")
    
    def consultar_um(self, sql: str, parametros: tuple = None) -> Optional[Dict]:
        """
        Executa uma query que retorna um resultado.
        
        Args:
            sql (str): Query SQL
            parametros (tuple): Parâmetros da query
            
        Returns:
            Dict: Um dicionário com os dados ou None
        """
        cursor = self._obter_cursor()
        if parametros:
            cursor.execute(sql, parametros)
        else:
            cursor.execute(sql)
        
        linha = cursor.fetchone()
        return dict(linha) if linha else None
    
    def consultar_todos(self, sql: str, parametros: tuple = None) -> List[Dict]:
        """
        Executa uma query que retorna múltiplos resultados.
        
        Args:
            sql (str): Query SQL
            parametros (tuple): Parâmetros da query
            
        Returns:
            List[Dict]: Lista de dicionários com os dados
        """
        cursor = self._obter_cursor()
        if parametros:
            cursor.execute(sql, parametros)
        else:
            cursor.execute(sql)
        
        linhas = cursor.fetchall()
        return [dict(linha) for linha in linhas]


class EstacoesRepository(BaseRepository):
    """Repositório para a tabela de Estações."""
    
    def inserir(self, id_municipio: str, id_estacao: str, estacao: str,
                data_fundacao: date, latitude: float, longitude: float,
                altitude: float) -> int:
        """
        Insere uma nova estação.
        
        Args:
            id_municipio (str): ID do município
            id_estacao (str): ID da estação (chave primária)
            estacao (str): Nome da estação
            data_fundacao (date): Data de fundação
            latitude (float): Latitude
            longitude (float): Longitude
            altitude (float): Altitude
            
        Returns:
            int: ID da estação inserida
        """
        sql = """
            INSERT INTO estacoes 
            (id_municipio, id_estacao, estacao, data_fundacao, latitude, longitude, altitude)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        parametros = (id_municipio, id_estacao, estacao, data_fundacao, 
                     latitude, longitude, altitude)
        return self.executar(sql, parametros)
    
    def obter_por_id(self, id_estacao: str) -> Optional[Dict]:
        """
        Obtém uma estação pelo ID.
        
        Args:
            id_estacao (str): ID da estação
            
        Returns:
            Dict: Dados da estação ou None
        """
        sql = "SELECT * FROM estacoes WHERE id_estacao = ?"
        return self.consultar_um(sql, (id_estacao,))
    
    def listar_todas(self) -> List[Dict]:
        """
        Lista todas as estações.
        
        Returns:
            List[Dict]: Lista de todas as estações
        """
        sql = "SELECT * FROM estacoes ORDER BY estacao"
        return self.consultar_todos(sql)
    
    def listar_por_municipio(self, id_municipio: str) -> List[Dict]:
        """
        Lista estações de um município.
        
        Args:
            id_municipio (str): ID do município
            
        Returns:
            List[Dict]: Lista de estações do município
        """
        sql = "SELECT * FROM estacoes WHERE id_municipio = ? ORDER BY estacao"
        return self.consultar_todos(sql, (id_municipio,))
    
    def atualizar(self, id_estacao: str, **kwargs) -> int:
        """
        Atualiza dados de uma estação.
        
        Args:
            id_estacao (str): ID da estação
            **kwargs: Campos a atualizar (estacao, latitude, longitude, altitude, etc)
            
        Returns:
            int: Número de linhas afetadas
        """
        campos_permitidos = {'id_municipio', 'estacao', 'data_fundacao', 
                           'latitude', 'longitude', 'altitude'}
        
        campos = {k: v for k, v in kwargs.items() if k in campos_permitidos}
        
        if not campos:
            raise ValueError("Nenhum campo válido para atualizar")
        
        set_clause = ", ".join([f"{k} = ?" for k in campos.keys()])
        sql = f"UPDATE estacoes SET {set_clause} WHERE id_estacao = ?"
        
        parametros = tuple(campos.values()) + (id_estacao,)
        cursor = self._obter_cursor()
        cursor.execute(sql, parametros)
        self.conexao.commit()
        return cursor.rowcount
    
    def deletar(self, id_estacao: str) -> int:
        """
        Deleta uma estação.
        
        Args:
            id_estacao (str): ID da estação
            
        Returns:
            int: Número de linhas deletadas
        """
        sql = "DELETE FROM estacoes WHERE id_estacao = ?"
        cursor = self._obter_cursor()
        cursor.execute(sql, (id_estacao,))
        self.conexao.commit()
        return cursor.rowcount
    
    def contar(self) -> int:
        """
        Conta o número total de estações.
        
        Returns:
            int: Total de estações
        """
        sql = "SELECT COUNT(*) as total FROM estacoes"
        resultado = self.consultar_um(sql)
        return resultado['total']


class MicrodadosRepository(BaseRepository):
    """Repositório para a tabela de Microdados."""
    
    def inserir(self, ano: int, mes: int, data: date, hora: str,
                id_estacao: str, precipitacao_total: float = None,
                pressao_atm_hora: float = None, pressao_atm_max: float = None,
                pressao_atm_min: float = None, radiacao_global: float = None,
                temperatura_bulbo_hora: float = None, temperatura_orvalho_hora: float = None,
                temperatura_max: float = None, temperatura_min: float = None,
                temperatura_orvalho_max: float = None, temperatura_orvalho_min: float = None,
                umidade_rel_max: float = None, umidade_rel_min: float = None,
                umidade_rel_hora: float = None, vento_direcao: float = None,
                vento_rajada_max: float = None, vento_velocidade: float = None) -> int:
        """
        Insere um novo registro de microdados.
        
        Args:
            ano (int): Ano
            mes (int): Mês
            data (date): Data
            hora (str): Hora
            id_estacao (str): ID da estação
            **kwargs: Outros campos climáticos
            
        Returns:
            int: ID do registro inserido
        """
        sql = """
            INSERT INTO microdados 
            (ano, mes, data, hora, id_estacao, precipitacao_total, pressao_atm_hora,
             pressao_atm_max, pressao_atm_min, radiacao_global, temperatura_bulbo_hora,
             temperatura_orvalho_hora, temperatura_max, temperatura_min, 
             temperatura_orvalho_max, temperatura_orvalho_min, umidade_rel_max,
             umidade_rel_min, umidade_rel_hora, vento_direcao, vento_rajada_max,
             vento_velocidade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        parametros = (ano, mes, data, hora, id_estacao, precipitacao_total,
                     pressao_atm_hora, pressao_atm_max, pressao_atm_min,
                     radiacao_global, temperatura_bulbo_hora, temperatura_orvalho_hora,
                     temperatura_max, temperatura_min, temperatura_orvalho_max,
                     temperatura_orvalho_min, umidade_rel_max, umidade_rel_min,
                     umidade_rel_hora, vento_direcao, vento_rajada_max, vento_velocidade)
        
        return self.executar(sql, parametros)
    
    def listar_por_estacao_periodo(self, id_estacao: str, data_inicio: date,
                                   data_fim: date) -> List[Dict]:
        """
        Lista microdados de uma estação em um período.
        
        Args:
            id_estacao (str): ID da estação
            data_inicio (date): Data inicial
            data_fim (date): Data final
            
        Returns:
            List[Dict]: Dados do período
        """
        sql = """
            SELECT * FROM microdados
            WHERE id_estacao = ? AND data BETWEEN ? AND ?
            ORDER BY data, hora
        """
        return self.consultar_todos(sql, (id_estacao, data_inicio, data_fim))
    
    def listar_por_estacao_ano(self, id_estacao: str, ano: int) -> List[Dict]:
        """
        Lista microdados de uma estação para um ano específico.
        
        Args:
            id_estacao (str): ID da estação
            ano (int): Ano
            
        Returns:
            List[Dict]: Dados do ano
        """
        sql = """
            SELECT * FROM microdados
            WHERE id_estacao = ? AND ano = ?
            ORDER BY mes, data, hora
        """
        return self.consultar_todos(sql, (id_estacao, ano))
    
    def listar_por_estacao_mes(self, id_estacao: str, ano: int, mes: int) -> List[Dict]:
        """
        Lista microdados de uma estação para um mês específico.
        
        Args:
            id_estacao (str): ID da estação
            ano (int): Ano
            mes (int): Mês
            
        Returns:
            List[Dict]: Dados do mês
        """
        sql = """
            SELECT * FROM microdados
            WHERE id_estacao = ? AND ano = ? AND mes = ?
            ORDER BY data, hora
        """
        return self.consultar_todos(sql, (id_estacao, ano, mes))
    
    def obter_media_temperatura(self, id_estacao: str, data_inicio: date,
                               data_fim: date) -> Optional[Dict]:
        """
        Calcula media de temperaturas em um período.
        
        Args:
            id_estacao (str): ID da estação
            data_inicio (date): Data inicial
            data_fim (date): Data final
            
        Returns:
            Dict: Médias de temperatura
        """
        sql = """
            SELECT 
                AVG(temperatura_bulbo_hora) as media_bulbo,
                AVG(temperatura_max) as media_max,
                AVG(temperatura_min) as media_min,
                MAX(temperatura_max) as temperatura_maxima,
                MIN(temperatura_min) as temperatura_minima
            FROM microdados
            WHERE id_estacao = ? AND data BETWEEN ? AND ?
        """
        return self.consultar_um(sql, (id_estacao, data_inicio, data_fim))
    
    def obter_precipitacao_total(self, id_estacao: str, data_inicio: date,
                                data_fim: date) -> Optional[float]:
        """
        Calcula precipitação total em um período.
        
        Args:
            id_estacao (str): ID da estação
            data_inicio (date): Data inicial
            data_fim (date): Data final
            
        Returns:
            float: Precipitação total
        """
        sql = """
            SELECT SUM(precipitacao_total) as total
            FROM microdados
            WHERE id_estacao = ? AND data BETWEEN ? AND ?
        """
        resultado = self.consultar_um(sql, (id_estacao, data_inicio, data_fim))
        return resultado['total'] if resultado else 0
    
    def deletar_por_periodo(self, id_estacao: str, data_inicio: date,
                           data_fim: date) -> int:
        """
        Deleta microdados de um período.
        
        Args:
            id_estacao (str): ID da estação
            data_inicio (date): Data inicial
            data_fim (date): Data final
            
        Returns:
            int: Número de registros deletados
        """
        sql = """
            DELETE FROM microdados
            WHERE id_estacao = ? AND data BETWEEN ? AND ?
        """
        cursor = self._obter_cursor()
        cursor.execute(sql, (id_estacao, data_inicio, data_fim))
        self.conexao.commit()
        return cursor.rowcount
    
    def contar_por_estacao(self, id_estacao: str) -> int:
        """
        Conta registros de microdados por estação.
        
        Args:
            id_estacao (str): ID da estação
            
        Returns:
            int: Total de registros
        """
        sql = "SELECT COUNT(*) as total FROM microdados WHERE id_estacao = ?"
        resultado = self.consultar_um(sql, (id_estacao,))
        return resultado['total']
    
    def contar_total(self) -> int:
        """
        Conta o número total de registros de microdados.
        
        Returns:
            int: Total de registros
        """
        sql = "SELECT COUNT(*) as total FROM microdados"
        resultado = self.consultar_um(sql)
        return resultado['total']

