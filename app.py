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


# ── Popover bimodal de referência fotográfica ─────────────────────────────────
def popover_referencia(caracteristica: str, caminho_imagem: Path) -> None:
    """
    Popover bimodal: painel esquerdo com a foto, painel direito com o zoom.
    Abre como flutuante ao clicar no botão ⓘ — sem tomar a página inteira.
    """
    with st.popover(f"ⓘ  {caracteristica}", use_container_width=False):
        painel_foto, painel_zoom = st.columns([0.7, 0.3])

        with painel_zoom:
            st.markdown("**🔍 Zoom**")
            zoom = st.slider(
                "zoom",
                min_value=25,
                max_value=200,
                value=100,
                step=25,
                format="%d%%",
                label_visibility="collapsed",
                key=f"zoom_{caracteristica}",
            )
            st.caption(
                "Drosophila melanogaster  \n"
                "André Karwath  \n"
                "CC BY-SA 2.5, Wikimedia Commons"
            )

        with painel_foto:
            largura = int(420 * zoom / 100)
            st.image(str(caminho_imagem), width=largura)


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

        # Popover bimodal fica acima do campo quando há foto disponível
        if tem_foto:
            popover_referencia(c, FOTOS_REFERENCIA[c.lower()])

        # Campo de entrada da característica
        if c.lower() == "i. costal":
            valor = st.text_input(c, placeholder="Digite o valor observado")
        else:
            opcoes = df[c].dropna().unique()
            valor  = st.selectbox(c, ["Desconhecido"] + list(opcoes), key=c)

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
