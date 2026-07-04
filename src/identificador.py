import pandas as pd
from pathlib import Path

# Caminho absoluto para o CSV, resolvido em relação a este arquivo
CAMINHO_DADOS = Path(__file__).parent.parent / "data" / "chave.csv"


def carregar_dados() -> pd.DataFrame:
    """
    Carrega a base de dados da chave taxonômica a partir do CSV.
    Remove espaços extras dos valores de texto para evitar duplicatas
    nas opções exibidas na interface (o CSV original não é alterado).
    """
    df = pd.read_csv(CAMINHO_DADOS)
    # Normaliza espaços em todas as colunas de texto:
    # - remove espaços no início e no fim (strip)
    # - colapsa espaços duplos internos para um único espaço
    # Corrige casos como 'castanho  (mel)' e 'castanho (mel)',
    # 'finas  (escuras)' e 'finas (escuras)', etc.
    colunas_texto = df.select_dtypes(include="object").columns
    df[colunas_texto] = df[colunas_texto].apply(
        lambda col: col.str.strip().str.replace(r"\s+", " ", regex=True)
    )
    return df


def calcular_similaridade(linha: pd.Series, entrada: dict, caracteristicas) -> float:
    """
    Calcula a similaridade morfológica entre uma espécie da base de dados
    e as características informadas pelo usuário.

    Ignora características marcadas como 'Desconhecido' ou vazias.
    Retorna um valor entre 0.0 (nenhuma correspondência) e 1.0 (correspondência total).
    """
    total = 0
    match = 0
    for c in caracteristicas:
        valor_usuario = str(entrada[c]).strip().lower()
        # Desconsidera características não informadas
        if valor_usuario == "" or valor_usuario == "desconhecido":
            continue
        total += 1
        valor_base = str(linha[c]).strip().lower()
        # Verifica se o valor do usuário está contido no valor da base
        if valor_usuario in valor_base:
            match += 1
    # Evita divisão por zero
    if total == 0:
        return 0.0
    return match / total
