import streamlit as st
import pandas as pd
from pathlib import Path
from src.identificador import carregar_dados, calcular_similaridade

# ── Configuração de caminhos ───────────────────────────────────────────────────
RAIZ    = Path(__file__).parent
VERSAO  = (RAIZ / "VERSION").read_text().strip()
PRANCHA = RAIZ / "prancha_fotografica"

# Atalho para a pasta de características observadas
OBS = PRANCHA / "caracteristicas_observadas"

# Configuração das abas por característica:
# { nome_em_minúsculas: [ (label_aba, título_acima_imagem, caminho_imagem) ] }
ABAS_POR_CARACTERISTICA = {
    "coloração": [
        (
            "🟡 Amarela",
            "Coloração amarela — corpo amarelo-claro a ocre",
            PRANCHA / "coloracao_referencia.jpg",
        ),
        (
            "⚫ Escura",
            "Coloração escura — corpo castanho-escuro a enegrecido",
            PRANCHA / "escura_referencia.jpg",
        ),
        (
            "🟤 Acastanhada",
            "Coloração acastanhada — tom intermediário acastanhado",
            PRANCHA / "acastanhada_referencia.jpg",
        ),
    ],
    "c.p. escutelares": [
        (
            "✅ Sim — Presentes",
            "Cerdas pré-escutelares presentes",
            OBS / "2c_p_escutelares" / "cerdas_pre_escutelares_presentes.jpg",
        ),
        (
            "❌ Não — Ausentes",
            "Cerdas pré-escutelares ausentes",
            OBS / "2c_p_escutelares" / "cerdas_pre_escutelares_ausentes.jpg",
        ),
    ],
    "c.escutelares": [
        (
            "↔ Convergente",
            "Cerdas escutelares anteriores convergentes",
            OBS / "3c_escutelares" / "cerdas_escutelares_anteriores_convergentes.jpg",
        ),
        (
            "↗ Divergente",
            "Cerdas escutelares anteriores divergentes",
            OBS / "3c_escutelares" / "cerdas_escutelares_anteriores_divergentes.jpg",
        ),
    ],
}

# Conjunto de características que possuem referência fotográfica
FOTOS_REFERENCIA = set(ABAS_POR_CARACTERISTICA.keys())

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
def mostrar_referencia(caracteristica: str) -> None:
    """
    Modal com abas por opção da característica.
    Cada aba mostra: título descritivo → slider de zoom → imagem.
    O botão X para fechar é fornecido automaticamente pelo st.dialog.
    """
    abas_config = ABAS_POR_CARACTERISTICA[caracteristica.lower()]
    abas = st.tabs([label for label, _, _ in abas_config])

    for aba, (label, titulo, img_path) in zip(abas, abas_config):
        with aba:
            # Título acima da imagem indicando o que ela representa
            st.markdown(f"### {titulo}")
            st.divider()

            col_img, col_ctrl = st.columns([0.75, 0.25])

            with col_ctrl:
                st.markdown("**🔍 Zoom**")
                zoom = st.slider(
                    "zoom",
                    min_value=25,
                    max_value=200,
                    value=100,
                    step=25,
                    format="%d%%",
                    label_visibility="collapsed",
                    key=f"zoom_{caracteristica}_{label}",
                )
                st.caption(f"{zoom}%")

            with col_img:
                largura = int(580 * zoom / 100)
                st.image(str(img_path), width=largura)


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
                if st.button("ⓘ", key=f"info_{c}", help="Ver referência fotográfica"):
                    mostrar_referencia(c)

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
