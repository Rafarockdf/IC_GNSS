import os

caminho_pasta = r"C:\Users\rafam\Desktop\IC_GNSS\EstudoGNSS\dados\MGBH" 

def transformar_arquivo_em_txt(caminho_pasta):
    nomes_pastas = os.listdir(caminho_pasta)

    for nome in nomes_pastas:
        nomes_arquivos = os.listdir(os.path.join(caminho_pasta, nome))
        for arquivo in nomes_arquivos: 
            if arquivo.endswith('.trop'):
                caminho_arquivo = os.path.join(caminho_pasta, nome, arquivo)
                novo_nome = arquivo.replace('.trop', '.txt')
                novo_caminho = os.path.join(caminho_pasta, nome, novo_nome)
                os.rename(caminho_arquivo, novo_caminho)
                print(f"Renomeado: {caminho_arquivo} para {novo_caminho}")

transformar_arquivo_em_txt(caminho_pasta)