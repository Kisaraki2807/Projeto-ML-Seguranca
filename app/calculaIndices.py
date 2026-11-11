import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# CONFIGURAÇÃO DE DIRETÓRIOS
# ============================================================
# Pega o caminho do calculaIndices.py e sobe um nível para chegar na raiz
BASE_DIR = Path(__file__).resolve().parent.parent

# Aponta para a pasta de dados
DATA_DIR = BASE_DIR / "data"

# Arquivos de entrada e saída
ARQUIVO_ENTRADA = DATA_DIR / "PENSE_2024_MICRODADOS-tratado2.csv"
ARQUIVO_SAIDA = DATA_DIR / "risco_capitais.csv"

# ============================================================
# MATRIZ DE RISCO
# ============================================================
grave = ['B06001A', 'B0600701', 'B0600702', 'B0600703', 'B06002A', 'B06003B', 'B07012A', 'E01P80', 'E01P82', 'E01P83', 'E01P84', 'E01P59A1', 'E01P59A2', 'B09002', 'B09004', 'B09005', 'B09010B203', 'B09010B204', 'B09010B205', 'B09010B206', 'B09016A1', 'B09016A2', 'B09018', 'B09017B101', 'B09017B102', 'B09017B103', 'B09017B104', 'B09017B105', 'B09017B106', 'B09017B201', 'B09017B202', 'B09017B203', 'B09017B204', 'B09017B205', 'B09017B206', 'B12008', 'B12009', 'B09012A3']
alto = ['B07007B', 'B07008A01', 'B07008A02', 'B07008A03', 'B07008A04', 'B07008A05', 'B07008A06', 'B07008A07', 'B07008A08', 'B07008A09', 'B07008A10', 'B07013', 'B07009', 'B0701401', 'B0701402', 'B0701403', 'B0701404', 'B0701405', 'B0701406', 'B0701407', 'B0701408', 'B0701409', 'B0701410', 'B07016', 'E01P79', 'E01P81A', 'B07015', 'B09003A', 'B09010A1', 'B09010B201', 'B09010B202', 'B09010B207', 'B09011A', 'B09012A1', 'B09014B', 'B09013B', 'B09001', 'B09012A2']
moderado = ['B04009B', 'B04010', 'B04016', 'B05007A', 'B05009A', 'B05004A', 'B05010A', 'B07011A', 'B12005', 'B12006']
leve = ['E01P23', 'B13005', 'B13006', 'B04001', 'B04003', 'B05003A', 'B05002A', 'B07001', 'B07002', 'B07005', 'B11007', 'B12007', 'B07004', 'B07006']

ibge_uf = {
    11: ('RO', 'Porto Velho'), 12: ('AC', 'Rio Branco'), 13: ('AM', 'Manaus'), 14: ('RR', 'Boa Vista'),
    15: ('PA', 'Belém'), 16: ('AP', 'Macapá'), 17: ('TO', 'Palmas'), 21: ('MA', 'São Luís'),
    22: ('PI', 'Teresina'), 23: ('CE', 'Fortaleza'), 24: ('RN', 'Natal'), 25: ('PB', 'João Pessoa'),
    26: ('PE', 'Recife'), 27: ('AL', 'Maceió'), 28: ('SE', 'Aracaju'), 29: ('BA', 'Salvador'),
    31: ('MG', 'Belo Horizonte'), 32: ('ES', 'Vitória'), 33: ('RJ', 'Rio de Janeiro'), 35: ('SP', 'São Paulo'),
    41: ('PR', 'Curitiba'), 42: ('SC', 'Florianópolis'), 43: ('RS', 'Porto Alegre'), 50: ('MS', 'Campo Grande'),
    51: ('MT', 'Cuiabá'), 52: ('GO', 'Goiânia'), 53: ('DF', 'Brasília')
}

def gerar_indices():
    if not ARQUIVO_ENTRADA.exists():
        print(f"ERRO: Arquivo não encontrado em {ARQUIVO_ENTRADA}")
        return

    print("Lendo microdados...")
    # Tenta usar vírgula; se não tiver colunas suficientes, usa ponto e vírgula
    df = pd.read_csv(ARQUIVO_ENTRADA, low_memory=False)
    if len(df.columns) < 5:
        df = pd.read_csv(ARQUIVO_ENTRADA, sep=';', low_memory=False)
        
    if 'CAPITAL' in df.columns:
        df = df[df['CAPITAL'] == 1].copy()
    
    todas_cols = grave + alto + moderado + leve
    
    # 1. Tratamento de Dados Ausentes
    for c in todas_cols:
        if c in df.columns:
            df.loc[df[c] < 0, c] = np.nan
            
    # 2. Inversão dos Fatores de Proteção
    para_inverter = ['B07004', 'B07006']
    for c in para_inverter:
        if c in df.columns:
            df[c] = 6 - df[c]

    print("Calculando o Risco Base por aluno...")
    df['media_grave'] = df[[c for c in grave if c in df.columns]].mean(axis=1)
    df['media_alto'] = df[[c for c in alto if c in df.columns]].mean(axis=1)
    df['media_mod'] = df[[c for c in moderado if c in df.columns]].mean(axis=1)
    df['media_leve'] = df[[c for c in leve if c in df.columns]].mean(axis=1)

    # 4. Cálculo Ponderado Final
    df['pontuacao_aluno'] = (
        (df['media_grave'].fillna(0) * 4) +
        (df['media_alto'].fillna(0) * 3) +
        (df['media_mod'].fillna(0) * 2) +
        (df['media_leve'].fillna(0) * 1)
    )

    print("Agrupando por Capital...")
    # 5. Agrupa a pontuação média por Capital (UF)
    df_capitais = df.groupby('UF')['pontuacao_aluno'].mean().reset_index()

    # 6. Normalização (Min-Max Scaling ajustado entre 0.1 e 0.9)
    p_min = df_capitais['pontuacao_aluno'].min()
    p_max = df_capitais['pontuacao_aluno'].max()
    df_capitais['risco_base'] = 0.1 + ((df_capitais['pontuacao_aluno'] - p_min) / (p_max - p_min)) * 0.8

    # 7. Mapeia UF e Capital
    df_capitais['uf'] = df_capitais['UF'].map(lambda x: ibge_uf.get(x, (None, None))[0])
    df_capitais['capital'] = df_capitais['UF'].map(lambda x: ibge_uf.get(x, (None, None))[1])
    
    # 8. Exportação
    df_final = df_capitais[['uf', 'capital', 'risco_base']].dropna()
    df_final.to_csv(ARQUIVO_SAIDA, index=False)
    
    print(f"Sucesso! O arquivo foi salvo em: {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    gerar_indices()