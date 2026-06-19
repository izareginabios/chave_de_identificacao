import streamlit as st
import pandas as pd
from pathlib import Path
from src.identificador import carregar_dados, calcular_similaridade

# ── Configuração de caminhos ───────────────────────────────────────────────────
RAIZ    = Path(__file__).parent
VERSAO  = (RAIZ / "VERSION").read_text().strip()
PRANCHA = RAIZ / "prancha_fotografica"
OBS     = PRANCHA / "caracteristicas_observadas"

# Abas do modal: { característica: [ (label_aba, título_acima, imagem) ] }
ABAS_POR_CARACTERISTICA = {
    "coloração": [
        ("🟡 Amarela",     "Coloração amarela",     PRANCHA / "coloracao_referencia.jpg"),
        ("⚫ Escura",      "Coloração escura",       PRANCHA / "escura_referencia.jpg"),
        ("🟤 Acastanhada", "Coloração acastanhada",  PRANCHA / "acastanhada_referencia.jpg"),
    ],
    "c.p. escutelares": [
        ("✅ Presentes", "Cerdas pré-escutelares presentes",      OBS / "2c_p_escutelares" / "cerdas_pre_escutelares_presentes.jpg"),
        ("❌ Ausentes",  "Ausência de cerdas pré-escutelares",    OBS / "2c_p_escutelares" / "cerdas_pre_escutelares_ausentes.jpg"),
    ],
    "c.escutelares": [
        ("↔ Convergente", "Cerdas escutelares anteriores convergentes", OBS / "3c_escutelares" / "cerdas_escutelares_anteriores_convergentes.jpg"),
        ("↗ Divergente",  "Cerdas escutelares anteriores divergentes",  OBS / "3c_escutelares" / "cerdas_escutelares_anteriores_divergentes.jpg"),
    ],
}

FOTOS_REFERENCIA = set(ABAS_POR_CARACTERISTICA.keys())

# ── Configuração da página ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Identificador de Drosofílideos",
    page_icon="🪰",
    layout="wide",
)

# ── Tema visual profissional ───────────────────────────────────────────────────
st.markdown("""
<style>
/* Fundo geral */
.stApp { background-color: #f0f3f8; }

/* Botão ⓘ — circular e discreto */
[data-testid="stColumn"] [data-testid="stButton"] button {
    margin-top: 1.55rem;
    height: 2rem; width: 2rem;
    padding: 0;
    border-radius: 50%;
    font-size: 0.95rem;
    min-height: unset;
    background-color: #dce8f7;
    color: #1a3d6e;
    border: 1px solid #b0c8e8;
    line-height: 1;
}
[data-testid="stColumn"] [data-testid="stButton"] button:hover {
    background-color: #1a3d6e;
    color: white;
    border-color: #1a3d6e;
}

/* Botão principal de identificação */
div[data-testid="stButton"] button[kind="primaryFormSubmit"],
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, #1a3d6e 0%, #2d6aad 100%);
    color: white;
    border: none;
    border-radius: 0.5rem;
    font-size: 1rem;
    font-weight: 600;
    padding: 0.55rem 2rem;
    box-shadow: 0 2px 6px rgba(26,61,110,0.25);
}

/* Cards das seções */
div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] {
    border-radius: 0.5rem;
}

/* Selectbox e inputs — bordas suaves */
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] input {
    border-radius: 0.4rem !important;
}

/* Métricas de resultado */
[data-testid="stMetric"] {
    background: white;
    border-radius: 0.6rem;
    padding: 1rem 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)


# ── Modal de referência fotográfica ───────────────────────────────────────────
@st.dialog("Referência Fotográfica", width="large")
def mostrar_referencia(caracteristica: str) -> None:
    """Modal com abas por opção da característica e slider de zoom."""
    abas_config = ABAS_POR_CARACTERISTICA[caracteristica.lower()]
    abas = st.tabs([label for label, _, _ in abas_config])

    for aba, (label, titulo, img_path) in zip(abas, abas_config):
        with aba:
            st.markdown(f"#### {titulo}")
            st.divider()
            col_img, col_ctrl = st.columns([0.78, 0.22])
            with col_ctrl:
                st.markdown("**🔍 Zoom**")
                zoom = st.slider(
                    "zoom",
                    min_value=25, max_value=150, value=100, step=25,
                    format="%d%%", label_visibility="collapsed",
                    key=f"zoom_{caracteristica}_{label}",
                )
            with col_img:
                st.image(str(img_path), width=int(640 * zoom / 100))


# ── Dados ──────────────────────────────────────────────────────────────────────
@st.cache_data
def obter_dados() -> pd.DataFrame:
    return carregar_dados()

df             = obter_dados()
coluna_especie = df.columns[0]
caracteristicas = df.columns[1:]

# ── Cabeçalho profissional ─────────────────────────────────────────────────────
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #1a3d6e 0%, #2d6aad 100%);
    padding: 2rem 2.5rem;
    border-radius: 0.85rem;
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0 3px 12px rgba(26,61,110,0.3);
">
    <h1 style="margin:0 0 0.35rem; font-size:1.9rem; font-weight:700; letter-spacing:-0.02em;">
        🪰 Identificador de Espécies de Drosofílideos
    </h1>
    <p style="margin:0; font-size:1rem; opacity:0.88; line-height:1.5;">
        Sistema digital de identificação taxonômica baseado em características morfológicas
    </p>
    <p style="margin:0.6rem 0 0; font-size:0.78rem; opacity:0.55; letter-spacing:0.03em;">
        versão {VERSAO}
    </p>
</div>
""", unsafe_allow_html=True)

# ── Seção de entrada ───────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: white;
    border-radius: 0.75rem;
    padding: 1.4rem 1.8rem 0.5rem;
    box-shadow: 0 1px 5px rgba(0,0,0,0.07);
    margin-bottom: 1rem;
">
    <h3 style="margin:0 0 0.2rem; color:#1a3d6e; font-size:1.05rem; font-weight:600;">
        📋 Características observadas
    </h3>
    <p style="margin:0 0 1rem; color:#555; font-size:0.88rem;">
        Selecione ou digite as características morfológicas do espécime.
        Clique em <strong>ⓘ</strong> para ver a referência fotográfica.
    </p>
</div>
""", unsafe_allow_html=True)

entrada_usuario = {}
num_colunas = 3
cols = st.columns(num_colunas)

for i, c in enumerate(caracteristicas):
    with cols[i % num_colunas]:
        tem_foto = c.lower() in FOTOS_REFERENCIA

        if tem_foto:
            col_campo, col_info = st.columns([0.83, 0.17])
        else:
            col_campo = st.container()

        with col_campo:
            if c.lower() == "i. costal":
                valor = st.text_input(c, placeholder="Digite o valor numérico")
            else:
                opcoes = df[c].dropna().unique()
                valor  = st.selectbox(c, ["Desconhecido"] + list(opcoes), key=c)

        if tem_foto:
            with col_info:
                if st.button("ⓘ", key=f"info_{c}", help="Ver referência fotográfica"):
                    mostrar_referencia(c)

        entrada_usuario[c] = valor

st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

# ── Botão de identificação ─────────────────────────────────────────────────────
col_btn, _ = st.columns([0.25, 0.75])
with col_btn:
    identificar = st.button("🔍 Identificar Espécie", type="primary", use_container_width=True)

st.divider()

# ── Resultados ─────────────────────────────────────────────────────────────────
if identificar:
    resultados = [
        {
            "Espécie": linha[coluna_especie],
            "Similaridade": calcular_similaridade(linha, entrada_usuario, caracteristicas),
        }
        for _, linha in df.iterrows()
    ]

    resultados = pd.DataFrame(resultados).sort_values("Similaridade", ascending=False)
    melhor     = resultados.iloc[0]

    if melhor["Similaridade"] == 0:
        st.warning("⚠️ Dados insuficientes para identificação. Selecione pelo menos uma característica.")
        st.stop()

    # Destaque do resultado principal
    sim_pct = round(melhor["Similaridade"] * 100, 1)
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1b6f3c 0%, #28a056 100%);
        color: white; padding: 1.3rem 1.8rem;
        border-radius: 0.75rem; margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(27,111,60,0.25);
    ">
        <p style="margin:0 0 0.2rem; font-size:0.85rem; opacity:0.8; font-weight:500;">
            ESPÉCIE MAIS PROVÁVEL
        </p>
        <p style="margin:0; font-size:1.5rem; font-weight:700; font-style:italic;">
            {melhor['Espécie']}
        </p>
        <p style="margin:0.3rem 0 0; font-size:0.95rem; opacity:0.9;">
            Similaridade morfológica: <strong>{sim_pct}%</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Top 5
    st.markdown("#### 🔬 Espécies com maior similaridade")
    top5 = resultados.head(5).copy()
    top5["Similaridade (%)"] = (top5["Similaridade"] * 100).round(1)
    st.dataframe(
        top5[["Espécie", "Similaridade (%)"]],
        use_container_width=True,
        hide_index=True,
    )

    # Ranking completo (expansível)
    with st.expander("📊 Ver ranking completo"):
        ranking = resultados.copy()
        ranking["Similaridade (%)"] = (ranking["Similaridade"] * 100).round(1)
        st.dataframe(ranking[["Espécie", "Similaridade (%)"]], use_container_width=True, hide_index=True)

    # Gráfico
    st.markdown("#### 📈 Gráfico de similaridade")
    st.bar_chart(resultados.set_index("Espécie")["Similaridade"])
