# ==========================================================
# IDENTIFICADOR DE ESPÉCIES DE DROSOPHILA
# Sistema baseado em regras (sem Machine Learning)
# Tiago Henrique - 15-03-2026
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data
def carregar_dados():
    df = pd.read_csv("chave.csv")
    return df
df = carregar_dados()
coluna_especie = df.columns[0]
caracteristicas = df.columns[1:]
st.title("Identificador de Espécies de Drosophila")
st.write(
"""
Sistema digital de identificação taxonômica baseado em
características morfológicas.
"""
)
st.warning("Teste")
st.success("Teste")
st.info("Teste")
st.divider()
st.subheader("Selecione ou digite as características observadas")
entrada_usuario = {}
num_colunas = 3
cols = st.columns(num_colunas)
for i, c in enumerate(caracteristicas):
    with cols[i % num_colunas]:
        if c.lower() == "i. costal":
            valor = st.text_input(
                c,
                placeholder="Digite o valor observado"
            )
        else:
            opcoes = df[c].dropna().unique()
            valor = st.selectbox(
                c,
                ["Desconhecido"] + list(opcoes),
                key=c
            )
        entrada_usuario[c] = valor
def calcular_similaridade(linha, entrada):
    total = 0
    match = 0
    for c in caracteristicas:
        valor_usuario = str(entrada[c]).strip().lower()
        if valor_usuario == "" or valor_usuario == "desconhecido":
            continue
        total += 1
        valor_base = str(linha[c]).strip().lower()
        if valor_usuario in valor_base:
            match += 1
    if total == 0:
        return 0
    return match / total
st.divider()
if st.button("Identificar Espécie"):
    resultados = []
    for i, linha in df.iterrows():
        score = calcular_similaridade(linha, entrada_usuario)
        resultados.append({
            "Espécie": linha[coluna_especie],
            "Similaridade": score
        })
    resultados = pd.DataFrame(resultados)
    resultados = resultados.sort_values(
        "Similaridade",
        ascending=False
    )
    melhor = resultados.iloc[0]
    if melhor["Similaridade"] == 0:
        st.warning("Dados insuficientes para a classificação.")
        st.stop()
    else:
        st.subheader("Espécie mais provável")
        st.success(
            f"{melhor['Espécie']} "
            f"(similaridade {round(melhor['Similaridade']*100,1)}%)"
        )
        st.subheader("Espécies semelhantes")
        top5 = resultados.head(5).copy()
        top5["Similaridade (%)"] = top5["Similaridade"] * 100
        st.dataframe(
            top5[["Espécie", "Similaridade (%)"]],
            use_container_width=True
        )
        st.subheader("Gráfico de similaridade")
        st.bar_chart(
            resultados.set_index("Espécie")["Similaridade"]
        )
    st.subheader("Espécie mais provável")
    melhor = resultados.iloc[0]
    st.success(
        f"{melhor['Espécie']} "
        f"(similaridade {round(melhor['Similaridade']*100,1)}%)"
    )
    st.subheader("Espécies semelhantes")
    top5 = resultados.head(5).copy()
    top5["Similaridade (%)"] = top5["Similaridade"] * 100
    st.dataframe(
        top5[["Espécie", "Similaridade (%)"]],
        use_container_width=True
    )
    st.subheader("Ranking completo")
    resultados["Similaridade (%)"] = resultados["Similaridade"] * 100
    st.dataframe(
        resultados,
        use_container_width=True
    )
    st.subheader("Gráfico de similaridade")
    st.bar_chart(
        resultados.set_index("Espécie")["Similaridade"]
    )
