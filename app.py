import streamlit as st
import pandas as pd
from src.identificador import carregar_dados, calcular_similaridade

# Configura a página para usar a largura total da tela
st.set_page_config(layout="wide")


# Cache para evitar recarregar o CSV a cada interação
@st.cache_data
def obter_dados() -> pd.DataFrame:
    return carregar_dados()


df = obter_dados()

# Primeira coluna = espécies; demais colunas = características morfológicas
coluna_especie = df.columns[0]
caracteristicas = df.columns[1:]

# ── Cabeçalho ──────────────────────────────────────────────────────────────────
st.title("Identificador de Espécies de Drosofílideos")
st.write(
    "Sistema digital de identificação taxonômica baseado em características morfológicas."
)

st.warning("Teste")
st.success("Teste")
st.info("Teste")

st.divider()

# ── Entrada de características ─────────────────────────────────────────────────
st.subheader("Selecione ou digite as características observadas")

entrada_usuario = {}
num_colunas = 3
cols = st.columns(num_colunas)

for i, c in enumerate(caracteristicas):
    with cols[i % num_colunas]:
        # Índice costal aceita valor numérico livre; demais usam selectbox
        if c.lower() == "i. costal":
            valor = st.text_input(c, placeholder="Digite o valor observado")
        else:
            opcoes = df[c].dropna().unique()
            valor = st.selectbox(c, ["Desconhecido"] + list(opcoes), key=c)
        entrada_usuario[c] = valor

st.divider()

# ── Identificação ──────────────────────────────────────────────────────────────
if st.button("Identificar Espécie"):
    # Calcula a similaridade para cada espécie da base
    resultados = [
        {
            "Espécie": linha[coluna_especie],
            "Similaridade": calcular_similaridade(linha, entrada_usuario, caracteristicas),
        }
        for _, linha in df.iterrows()
    ]

    resultados = pd.DataFrame(resultados).sort_values("Similaridade", ascending=False)
    melhor = resultados.iloc[0]

    # Sem dados suficientes para identificar
    if melhor["Similaridade"] == 0:
        st.warning("Dados insuficientes para a classificação.")
        st.stop()

    # Espécie mais provável
    st.subheader("Espécie mais provável")
    st.success(
        f"{melhor['Espécie']} (similaridade {round(melhor['Similaridade'] * 100, 1)}%)"
    )

    # Top 5 espécies mais semelhantes
    st.subheader("Espécies semelhantes")
    top5 = resultados.head(5).copy()
    top5["Similaridade (%)"] = top5["Similaridade"] * 100
    st.dataframe(top5[["Espécie", "Similaridade (%)"]], use_container_width=True)

    # Ranking completo
    st.subheader("Ranking completo")
    resultados["Similaridade (%)"] = resultados["Similaridade"] * 100
    st.dataframe(resultados, use_container_width=True)

    # Gráfico de barras com todas as similaridades
    st.subheader("Gráfico de similaridade")
    st.bar_chart(resultados.set_index("Espécie")["Similaridade"])
