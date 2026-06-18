import streamlit as st
import pandas as pd
from pathlib import Path
from src.identificador import carregar_dados, calcular_similaridade

# ── Configuração de caminhos ───────────────────────────────────────────────────
RAIZ    = Path(__file__).parent
VERSAO  = (RAIZ / "VERSION").read_text().strip()
PRANCHA = RAIZ / "prancha_fotografica"

# Mapeamento: nome da característica (minúsculas) → imagem de referência
FOTOS_REFERENCIA = {
    "coloração": PRANCHA / "coloracao_referencia.jpg",
}

# ── Configuração da página ─────────────────────────────────────────────────────
st.set_page_config(page_title="Identificador de Drosofílideos", layout="wide")

# CSS: alinha o botão ⓘ com o label do campo ao lado
st.markdown(
    """
    <style>
    /* Empurra o botão ⓘ para baixo para alinhar com o label do selectbox */
    [data-testid="stColumn"] [data-testid="stButton"] button {
        margin-top: 1.55rem;
        padding: 0.15rem 0.5rem;
        font-size: 0.9rem;
        min-height: 2.1rem;
        border-radius: 0.5rem;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Modal de referência fotográfica ───────────────────────────────────────────
@st.dialog("Referência Fotográfica", width="large")
def mostrar_referencia(caracteristica: str, caminho_imagem: Path) -> None:
    """
    Abre um modal com a foto de referência da característica.
    O botão X para fechar é fornecido automaticamente pelo st.dialog.
    """
    st.markdown(f"**Característica: {caracteristica}**")

    # Barra de zoom
    zoom = st.slider(
        "🔍 Zoom",
        min_value=25,
        max_value=200,
        value=100,
        step=25,
        format="%d%%",
    )
    # Largura base de 650 px ajustada pelo zoom
    largura = int(650 * zoom / 100)

    st.image(
        str(caminho_imagem),
        width=largura,
        caption=(
            "Drosophila melanogaster — André Karwath "
            "(CC BY-SA 2.5, Wikimedia Commons)"
        ),
    )

    # Legenda explicativa das opções de coloração
    if caracteristica.lower() == "coloração":
        st.markdown(
            "**Opções de coloração:**\n\n"
            "- 🟡 **amarela** — corpo amarelo-claro a ocre\n"
            "- ⚫ **escura** — corpo castanho-escuro a enegrecido\n"
            "- 🟤 **acastanhada** — tom intermediário acastanhado"
        )


# ── Dados ──────────────────────────────────────────────────────────────────────
@st.cache_data
def obter_dados() -> pd.DataFrame:
    """Carrega e armazena em cache os dados da chave taxonômica."""
    return carregar_dados()


df            = obter_dados()
coluna_especie = df.columns[0]
caracteristicas = df.columns[1:]

# ── Cabeçalho ──────────────────────────────────────────────────────────────────
st.title("Identificador de Espécies de Drosofílideos")
st.caption(f"versão {VERSAO}")
st.write("Sistema digital de identificação taxonômica baseado em características morfológicas.")

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
        tem_foto = c.lower() in FOTOS_REFERENCIA

        if tem_foto:
            # Coluna larga para o campo + coluna estreita para o ⓘ
            col_campo, col_info = st.columns([0.83, 0.17])
        else:
            col_campo = st.container()

        with col_campo:
            # Índice costal aceita valor numérico livre; demais usam selectbox
            if c.lower() == "i. costal":
                valor = st.text_input(c, placeholder="Digite o valor observado")
            else:
                opcoes = df[c].dropna().unique()
                valor  = st.selectbox(c, ["Desconhecido"] + list(opcoes), key=c)

        if tem_foto:
            with col_info:
                # Abre o modal ao clicar no ⓘ
                if st.button("ⓘ", key=f"info_{c}", help="Ver referência fotográfica"):
                    mostrar_referencia(c, FOTOS_REFERENCIA[c.lower()])

        entrada_usuario[c] = valor

st.divider()

# ── Identificação ──────────────────────────────────────────────────────────────
if st.button("Identificar Espécie"):
    # Calcula similaridade morfológica para cada espécie da base
    resultados = [
        {
            "Espécie": linha[coluna_especie],
            "Similaridade": calcular_similaridade(linha, entrada_usuario, caracteristicas),
        }
        for _, linha in df.iterrows()
    ]

    resultados = pd.DataFrame(resultados).sort_values("Similaridade", ascending=False)
    melhor     = resultados.iloc[0]

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
