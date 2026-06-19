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
# { nome_em_minúsculas: [ (label_aba, título_acima, caminho_imagem, descrição_ao_lado) ] }
ABAS_POR_CARACTERISTICA = {
    "coloração": [
        (
            "🟡 Amarela",
            "Coloração amarela",
            PRANCHA / "coloracao_referencia.jpg",
            "Corpo de coloração amarela,\namarelo-claro a ocre.\nEx.: D. melanogaster",
        ),
        (
            "⚫ Escura",
            "Coloração escura",
            PRANCHA / "escura_referencia.jpg",
            "Corpo de coloração escura,\ncastanho-escuro a enegrecido.\nEx.: D. busckii",
        ),
        (
            "🟤 Acastanhada",
            "Coloração acastanhada",
            PRANCHA / "acastanhada_referencia.jpg",
            "Corpo de tom intermediário\nacastanhado.\nEx.: D. immigrans",
        ),
    ],
    "c.p. escutelares": [
        (
            "✅ Sim — Presentes",
            "Cerdas pré-escutelares presentes",
            OBS / "2c_p_escutelares" / "cerdas_pre_escutelares_presentes.jpg",
            "Cerdas pré-escutelares\npresentes",
        ),
        (
            "❌ Não — Ausentes",
            "Ausência de cerdas pré-escutelares",
            OBS / "2c_p_escutelares" / "cerdas_pre_escutelares_ausentes.jpg",
            "Ausência de cerdas\npré-escutelares",
        ),
    ],
    "c.escutelares": [
        (
            "↔ Convergente",
            "Cerdas escutelares anteriores convergentes",
            OBS / "3c_escutelares" / "cerdas_escutelares_anteriores_convergentes.jpg",
            "Cerdas escutelares\nanteriores convergentes",
        ),
        (
            "↗ Divergente",
            "Cerdas escutelares anteriores divergentes",
            OBS / "3c_escutelares" / "cerdas_escutelares_anteriores_divergentes.jpg",
            "Cerdas escutelares\nanteriores divergentes",
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
    abas = st.tabs([label for label, _, _, _ in abas_config])

    for aba, (label, titulo, img_path, descricao) in zip(abas, abas_config):
        with aba:
            # Título acima da imagem indicando o que ela representa
            st.markdown(f"### {titulo}")
            st.divider()

            col_img, col_ctrl = st.columns([0.72, 0.28])

            with col_ctrl:
                # Descrição do que a imagem mostra
                st.markdown(
                    f"<p style='font-size:0.95rem; line-height:1.5; "
                    f"padding:0.6rem 0.8rem; background:#f0f2f6; "
                    f"border-radius:0.4rem; margin-bottom:1rem;'>"
                    f"{descricao.replace(chr(10), '<br>')}</p>",
                    unsafe_allow_html=True,
                )
                st.markdown("**🔍 Zoom**")
                zoom = st.slider(
                    "zoom",
                    min_value=25,
                    max_value=150,
                    value=100,
                    step=25,
                    format="%d%%",
                    label_visibility="collapsed",
                    key=f"zoom_{caracteristica}_{label}",
                )

            with col_img:
                # Largura base 650 px — proporcional ao zoom selecionado
                st.image(str(img_path), width=int(650 * zoom / 100))


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
