"""
Exemplos de uso dos repositórios de Estações e Microdados.
"""

from datetime import date
from repositories import EstacõesRepository, MicrodadosRepository
from init_database import criar_banco_dados


def exemplo_estacoes():
    """Exemplos de uso do repositório de estações."""
    print("\n" + "="*60)
    print("EXEMPLOS - REPOSITÓRIO DE ESTAÇÕES")
    print("="*60)
    
    repo = EstacõesRepository()
    repo.conectar()
    
    try:
        # Inserir uma estação
        print("\n1. Inserindo uma estação...")
        repo.inserir(
            id_municipio='31',
            id_estacao='MGBH',
            estacao='Belo Horizonte',
            data_fundacao=date(2009, 1, 1),
            latitude=-19.93,
            longitude=-43.93,
            altitude=847.0
        )
        print("✓ Estação 'MGBH' inserida com sucesso!")
        
        # Inserir mais uma
        repo.inserir(
            id_municipio='32',
            id_estacao='MGMC',
            estacao='Montes Claros',
            data_fundacao=date(2010, 1, 1),
            latitude=-16.73,
            longitude=-43.85,
            altitude=645.0
        )
        print("✓ Estação 'MGMC' inserida com sucesso!")
        
        # Listar todas as estações
        print("\n2. Listando todas as estações...")
        estacoes = repo.listar_todas()
        for est in estacoes:
            print(f"  - {est['id_estacao']}: {est['estacao']} (Lat: {est['latitude']}, Long: {est['longitude']})")
        
        # Buscar por ID
        print("\n3. Buscando estação por ID...")
        estacao = repo.obter_por_id('MGBH')
        if estacao:
            print(f"✓ Estação encontrada: {estacao['estacao']}")
            print(f"  Latitude: {estacao['latitude']}")
            print(f"  Longitude: {estacao['longitude']}")
            print(f"  Altitude: {estacao['altitude']}m")
        
        # Atualizar dados
        print("\n4. Atualizando dados de estação...")
        repo.atualizar('MGBH', altitude=850.0)
        estacao_atualizada = repo.obter_por_id('MGBH')
        print(f"✓ Altitude atualizada para: {estacao_atualizada['altitude']}m")
        
        # Contar
        print("\n5. Contando estações...")
        total = repo.contar()
        print(f"✓ Total de estações: {total}")
        
    finally:
        repo.desconectar()


def exemplo_microdados():
    """Exemplos de uso do repositório de microdados."""
    print("\n" + "="*60)
    print("EXEMPLOS - REPOSITÓRIO DE MICRODADOS")
    print("="*60)
    
    repo = MicrodadosRepository()
    repo.conectar()
    
    try:
        # Inserir microdados
        print("\n1. Inserindo microdados...")
        repo.inserir(
            ano=2024,
            mes=1,
            data=date(2024, 1, 1),
            hora='00:00',
            id_estacao='MGBH',
            precipitacao_total=0.0,
            pressao_atm_hora=1013.25,
            temperatura_bulbo_hora=22.5,
            temperatura_max=28.3,
            temperatura_min=18.2,
            umidade_rel_hora=65.0,
            vento_velocidade=5.2
        )
        print("✓ Microdados de 01/01/2024 inseridos!")
        
        repo.inserir(
            ano=2024,
            mes=1,
            data=date(2024, 1, 2),
            hora='00:00',
            id_estacao='MGBH',
            precipitacao_total=2.5,
            pressao_atm_hora=1012.50,
            temperatura_bulbo_hora=21.8,
            temperatura_max=27.1,
            temperatura_min=17.5,
            umidade_rel_hora=72.0,
            vento_velocidade=4.8
        )
        print("✓ Microdados de 02/01/2024 inseridos!")
        
        # Listar por período
        print("\n2. Listando microdados do período 01/01 - 02/01/2024...")
        dados = repo.listar_por_estacao_periodo(
            'MGBH',
            date(2024, 1, 1),
            date(2024, 1, 2)
        )
        for dado in dados:
            print(f"  {dado['data']} {dado['hora']} - Temp: {dado['temperatura_bulbo_hora']}°C, Umidade: {dado['umidade_rel_hora']}%")
        
        # Listar por ano
        print("\n3. Listando todos os dados de 2024...")
        dados_ano = repo.listar_por_estacao_ano('MGBH', 2024)
        print(f"✓ Total de registros em 2024: {len(dados_ano)}")
        
        # Média de temperatura
        print("\n4. Calculando média de temperatura do período...")
        medias = repo.obter_media_temperatura(
            'MGBH',
            date(2024, 1, 1),
            date(2024, 1, 2)
        )
        if medias:
            print(f"  Média de temperatura: {medias['media_bulbo']:.2f}°C")
            print(f"  Temperatura máxima: {medias['temperatura_maxima']:.2f}°C")
            print(f"  Temperatura mínima: {medias['temperatura_minima']:.2f}°C")
        
        # Precipitação total
        print("\n5. Calculando precipitação total do período...")
        precip = repo.obter_precipitacao_total(
            'MGBH',
            date(2024, 1, 1),
            date(2024, 1, 2)
        )
        print(f"  Precipitação total: {precip:.2f}mm")
        
        # Contar
        print("\n6. Contando registros...")
        total = repo.contar_por_estacao('MGBH')
        print(f"✓ Total de registros da estação MGBH: {total}")
        
    finally:
        repo.desconectar()


if __name__ == "__main__":
    # Criar banco de dados
    print("Inicializando banco de dados...")
    criar_banco_dados()
    
    # Executar exemplos
    exemplo_estacoes()
    exemplo_microdados()
    
    print("\n" + "="*60)
    print("✓ Exemplos concluídos com sucesso!")
    print("="*60)
