import streamlit as st
import pandas as pd
from pathlib import Path
from src.identificador import carregar_dados, calcular_similaridade

# Versão do aplicativo
VERSAO = Path("VERSION").read_text().strip()

# Configura a página para usar a largura total da tela
st.set_page_config(
    page_title="Identificador de Drosofílideos",
    layout="wide",
)


# Cache para evitar recarregar o CSV a cada interação
@st.cache_data
def obter_dados() -> pd.DataFrame:
    return carregar_dados()


df = obter_dados()

# Primeira coluna = espécies; demais colunas = características morfológicas
coluna_especie = df.columns[0]
caracteristicas = df.columns[1:]

# Caminho para as imagens de referência da prancha fotográfica
PRANCHA = Path("prancha_fotografica")

# ── Cabeçalho ──────────────────────────────────────────────────────────────────
st.title("Identificador de Espécies de Drosofílideos")
st.caption(f"versão {VERSAO}")
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

        # Popover de referência fotográfica para a característica Coloração
        if c.lower() == "coloração":
            imagem_coloracao = PRANCHA / "coloracao_referencia.jpg"
            with st.popover("📷 ver referência fotográfica"):
                st.markdown("**Coloração do corpo em Drosophila**")
                st.image(
                    str(imagem_coloracao),
                    caption=(
                        "Drosophila melanogaster — coloração amarela típica do grupo melanogaster. "
                        "Foto: André Karwath (CC BY-SA 2.5, Wikimedia Commons)"
                    ),
                    use_container_width=True,
                )
                st.markdown(
                    "- **amarela** — corpo amarelo-claro a ocre\n"
                    "- **escura** — corpo castanho-escuro a enegrecido\n"
                    "- **acastanhada** — tom intermediário, acastanhado"
                )

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
