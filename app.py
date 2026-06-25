import streamlit as st
import pandas as pd
from pathlib import Path
from src.identificador import carregar_dados, calcular_similaridade

# ── Configuração de caminhos ───────────────────────────────────────────────────
RAIZ    = Path(__file__).parent
VERSAO  = (RAIZ / "VERSION").read_text().strip()
PRANCHA = RAIZ / "prancha_fotografica"
OBS     = PRANCHA / "caracteristicas_observadas"
ESP     = PRANCHA / "imagens_dos_drosofilideos"

# ── Abas do modal por característica ──────────────────────────────────────────
ABAS_POR_CARACTERISTICA = {
    "coloração": [
        ("Amarela",     "Coloração amarela",     PRANCHA / "coloracao_referencia.jpg"),
        ("Escura",      "Coloração escura",       PRANCHA / "escura_referencia.jpg"),
        ("Acastanhada", "Coloração acastanhada",  PRANCHA / "acastanhada_referencia.jpg"),
    ],
    "c.p. escutelares": [
        ("Presentes", "Cerdas pré-escutelares presentes",   OBS / "2c_p_escutelares" / "cerdas_pre_escutelares_presentes.jpg"),
        ("Ausentes",  "Ausência de cerdas pré-escutelares", OBS / "2c_p_escutelares" / "cerdas_pre_escutelares_ausentes.jpg"),
    ],
    "c.escutelares": [
        ("Convergente", "Cerdas escutelares anteriores convergentes", OBS / "3c_escutelares" / "cerdas_escutelares_anteriores_convergentes.jpg"),
        ("Divergente",  "Cerdas escutelares anteriores divergentes",  OBS / "3c_escutelares" / "cerdas_escutelares_anteriores_divergentes.jpg"),
    ],
    "c.cuneiformis": [
        ("Presentes", "Fileira de cerdas cuneiformes na parte interna do 1º fêmur", OBS / "4c_cuneiformis" / "4_fileira_de_cerdas_cuneiformes_na_parte_interna_do_primeiro_femur.jpg"),
        ("Ausentes",  "Sem cerdas cuneiformes no fêmur",                            OBS / "4c_cuneiformis" / "4_sem_cerdas_cuneiformes_no_femur.jpg"),
    ],
    "pentes sexuais": [
        ("Presentes",    "Pentes sexuais presentes",                              OBS / "5pentes_sexuais" / "5_pentes_sexuais.jpg"),
        ("Distribuídos", "Pentes sexuais distribuídos ao longo dos tarsos do macho", OBS / "5pentes_sexuais" / "5_pentes_sexuais_distribuidos_ao_longo_dos_tarsos_do_macho.jpg"),
    ],
    "i. costal": [
        ("Referência", "Índice costal — referência de medição", OBS / "6i_costal" / "6_indice_costal..jpg"),
    ],
}

FOTOS_REFERENCIA = set(ABAS_POR_CARACTERISTICA.keys())

# ── Mapeamento espécie → prancha fotográfica ───────────────────────────────────
FOTOS_ESPECIES = {
    "d. ananassae":     ESP / "d_ananassae.jpg",
    "d. maculifrons":   ESP / "D_maculifrons.jpg",
    "d. immigrans":     ESP / "D_immigrans (1).jpg",
    "d. annulimana":    ESP / "d_annulimana.jpg",
    "d. ararama":       ESP / "d_ararama.jpg",
    "d.austrosaltans":  ESP / "d_austrosaltans.jpg",
    "d. guaru":         ESP / "d_guaru.jpg",
    "d. hydei":         ESP / "d_hidey.jpg",
    "d. malerkotliana": ESP / "d_malerkotliana (1).jpg",
    "d. mediopicta":    ESP / "d_mediopicta.jpg",
    "d. melanogaster":  ESP / "d_melanogaster.jpg",
    "d. mercatorum":    ESP / "d_mercatorum (1).jpg",
}

# ── Configuração da página ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Identificador de Drosofílideos",
    page_icon="🪰",
    layout="wide",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Fundo geral */
.stApp { background-color: #f0f3f8; }

/* Borda cinza escuro nos campos de entrada */
[data-baseweb="select"] > div:first-child {
    border: 1.5px solid #555 !important;
    border-radius: 0.4rem !important;
}
[data-baseweb="input"] {
    border: 1.5px solid #555 !important;
    border-radius: 0.4rem !important;
}

/* Botão ⓘ — remove todos os estilos do framework */
[data-testid="stButton"] button[title="Ver referência fotográfica"] {
    all: unset;
    cursor: pointer;
    font-size: 0.9rem;
    opacity: 0.45;
    line-height: 1;
    display: inline;
}
[data-testid="stButton"] button[title="Ver referência fotográfica"]:hover {
    opacity: 0.9;
}

/* Botão principal */
button[kind="primary"] {
    background: linear-gradient(135deg, #1a3d6e 0%, #2d6aad 100%) !important;
    border: none !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 6px rgba(26,61,110,0.25) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Modal de referência fotográfica ───────────────────────────────────────────
@st.dialog("Referência Fotográfica", width="large")
def mostrar_referencia(caracteristica: str) -> None:
    abas_config = ABAS_POR_CARACTERISTICA[caracteristica.lower()]
    abas = st.tabs([label for label, _, _ in abas_config])

    for aba, (label, titulo, img_path) in zip(abas, abas_config):
        with aba:
            st.markdown(
                f"<h4 style='text-align:center; color:inherit; opacity:0.85; margin-bottom:0.6rem;'>"
                f"{titulo}</h4>",
                unsafe_allow_html=True,
            )
            # Imagem enquadrada em coluna central — largura moderada por padrão
            col_l, col_c, col_r = st.columns([0.2, 0.6, 0.2])
            with col_c:
                zoom = st.session_state.get(f"zoom_{caracteristica}_{label}", 75)
                st.image(str(img_path), width=int(480 * zoom / 100))

            # Zoom abaixo da imagem
            st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)
            col_zl, col_zm, col_zr = st.columns([0.2, 0.6, 0.2])
            with col_zm:
                st.slider(
                    "Zoom",
                    min_value=25, max_value=150, value=75, step=25,
                    format="%d%%",
                    key=f"zoom_{caracteristica}_{label}",
                )


# ── Dados ──────────────────────────────────────────────────────────────────────
@st.cache_data
def obter_dados() -> pd.DataFrame:
    return carregar_dados()

df              = obter_dados()
coluna_especie  = df.columns[0]
caracteristicas = df.columns[1:]

# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #1a3d6e 0%, #2d6aad 100%);
    padding: 2rem 2.5rem; border-radius: 0.85rem; color: white;
    margin-bottom: 1.5rem; box-shadow: 0 3px 12px rgba(26,61,110,0.3);
">
    <h1 style="margin:0 0 0.35rem; font-size:1.9rem; font-weight:700;">
        Identificador de Espécies de Drosofílideos
    </h1>
    <p style="margin:0; font-size:1rem; opacity:0.88;">
        Sistema digital de identificação taxonômica baseado em características morfológicas
    </p>
    <p style="margin:0.6rem 0 0; font-size:0.78rem; opacity:0.55;">versão {VERSAO}</p>
</div>
""", unsafe_allow_html=True)

# ── Seção de entrada ───────────────────────────────────────────────────────────
st.markdown("""
<div style="background:white; border-radius:0.75rem; padding:1.2rem 1.8rem 0.2rem;
            box-shadow:0 1px 5px rgba(0,0,0,0.07); margin-bottom:1rem;">
    <h3 style="margin:0 0 0.15rem; color:inherit; font-size:1.05rem; font-weight:600;">
        Características observadas
    </h3>
    <p style="margin:0 0 0.8rem; color:inherit; opacity:0.65; font-size:0.87rem;">
        Selecione as características do espécime. Clique em <strong>ⓘ</strong>
        ao lado do nome para ver a referência fotográfica.
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
            col_nome, col_btn = st.columns([0.82, 0.18])
            with col_nome:
                st.markdown(
                    f"<p style='margin:0; font-size:0.875rem; "
                    f"font-weight:600; color:inherit;'>{c}</p>",
                    unsafe_allow_html=True,
                )
            with col_btn:
                if st.button("ⓘ", key=f"info_{c}", help="Ver referência fotográfica"):
                    mostrar_referencia(c)

            if c.lower() == "i. costal":
                valor = st.text_input(
                    c, placeholder="Digite o valor numérico",
                    label_visibility="collapsed", key=f"input_{c}",
                )
            else:
                opcoes = df[c].dropna().unique()
                valor = st.selectbox(
                    c, ["Desconhecido"] + list(opcoes),
                    label_visibility="collapsed", key=c,
                )
        else:
            if c.lower() == "i. costal":
                valor = st.text_input(c, placeholder="Digite o valor numérico")
            else:
                opcoes = df[c].dropna().unique()
                valor = st.selectbox(c, ["Desconhecido"] + list(opcoes), key=c)

        entrada_usuario[c] = valor

st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)

# ── Botão de identificação ─────────────────────────────────────────────────────
col_btn, _ = st.columns([0.22, 0.78])
with col_btn:
    identificar = st.button("Identificar Espécie", type="primary", use_container_width=True)

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
        st.warning("Dados insuficientes. Selecione pelo menos uma característica.")
        st.stop()

    sim_pct      = round(melhor["Similaridade"] * 100, 1)
    nome_especie = melhor["Espécie"]

    # Banner do resultado principal
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1b6f3c 0%, #28a056 100%);
        color: white; padding: 1.3rem 1.8rem; border-radius: 0.75rem;
        margin-bottom: 1.2rem; box-shadow: 0 2px 8px rgba(27,111,60,0.25);
    ">
        <p style="margin:0 0 0.2rem; font-size:0.82rem; opacity:0.8; font-weight:500; letter-spacing:.05em;">
            ESPÉCIE MAIS PROVÁVEL
        </p>
        <p style="margin:0; font-size:1.55rem; font-weight:700; font-style:italic;">
            {nome_especie}
        </p>
        <p style="margin:0.3rem 0 0; font-size:0.95rem; opacity:0.9;">
            Similaridade morfológica: <strong>{sim_pct}%</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Prancha fotográfica da espécie (se disponível)
    foto_esp = FOTOS_ESPECIES.get(nome_especie.lower().strip())
    if foto_esp and foto_esp.exists():
        st.markdown(
            f"<h4 style='color:inherit; margin-bottom:0.5rem;'>"
            f"Prancha fotográfica — <em>{nome_especie}</em></h4>",
            unsafe_allow_html=True,
        )
        col_foto, col_info = st.columns([0.55, 0.45])
        with col_foto:
            st.image(str(foto_esp), caption=nome_especie, use_container_width=True)
        with col_info:
            st.markdown(f"""
            <div style="background:rgba(26,61,110,0.06); border-left:4px solid #2d6aad;
                        padding:1rem 1.2rem; border-radius:0 0.5rem 0.5rem 0;
                        margin-top:0.5rem;">
                <p style="margin:0; font-size:0.95rem; color:inherit; font-weight:600;">
                    {nome_especie}
                </p>
                <p style="margin:0.4rem 0 0; font-size:0.88rem; color:inherit; opacity:0.75;">
                    Similaridade: <strong>{sim_pct}%</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)

    # Top 5
    st.markdown("#### Espécies com maior similaridade")
    top5 = resultados.head(5).copy()
    top5["Similaridade (%)"] = (top5["Similaridade"] * 100).round(1)
    st.dataframe(top5[["Espécie", "Similaridade (%)"]], use_container_width=True, hide_index=True)

    # Ranking completo expansível
    with st.expander("Ver ranking completo"):
        ranking = resultados.copy()
        ranking["Similaridade (%)"] = (ranking["Similaridade"] * 100).round(1)
        st.dataframe(ranking[["Espécie", "Similaridade (%)"]], use_container_width=True, hide_index=True)

    # Gráfico
    st.markdown("#### Gráfico de similaridade")
    st.bar_chart(resultados.set_index("Espécie")["Similaridade"])
