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
        ("Amarela", "Coloração amarela", OBS / "1_coloracao" / "especies_amarelas.jpg"),
        ("Escura",  "Coloração escura",  OBS / "1_coloracao" / "especies_escuras.jpg"),
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

# Características sem foto ainda — exibem botão ⓘ com placeholder
PLACEHOLDERS_REFERENCIA = {
    "mesonoto cor",
    "mesonoto brilho/fosco",
    "faixas tergitos fêmeas (espessura e coloração)",
    "coloração escura últimos tergitos (macho)",
    "faixas tergitos interrompidas",
    "mancha nos últimos  tergitos macho",
    "mancha nos últimos  tergitos fêmeas",
    "veias transversais enfumaçadas",
}

# ── Grupos crípticos ──────────────────────────────────────────────────────────
GRUPOS_CRIPTICOS: dict[str, set[str]] = {
    "melanogaster": {
        "d. ananassae", "d. malerkotliana", "d. melanogaster", "d. simulans",
        "d. kikkawai", "d. suzukii",
    },
    "repleta": {
        "d. senei", "d. hydei", "d. mercatorum", "d. paranaensis",
        "d. antonietae", "d. buzzatii",
    },
    "willistoni": {
        "d. bocainensis", "d. capricorni", "d. nebulosa", "d. paulistorum",
    },
    "saltans": {
        "d. emarginata", "d. neoelliptica", "d. neosaltans", "d. austrosaltans",
        "d. prosaltans", "d. pseudosaltans", "d. dacunhai", "d. lehrmanae",
        "d. magalhaesis", "d. milleri", "d. sturtevanti",
    },
}
TODAS_CRIPTICAS: set[str] = {sp for g in GRUPOS_CRIPTICOS.values() for sp in g}

def grupo_criptico(nome: str) -> str | None:
    chave = nome.lower().strip()
    for grupo, especies in GRUPOS_CRIPTICOS.items():
        if chave in especies:
            return grupo
    return None

def nome_com_grupo(nome: str) -> str:
    g = grupo_criptico(nome)
    if g:
        return f"{nome} (grupo {g})"
    return nome

# ── Pasta de edeagos (imagens inseridas pelo administrador) ───────────────────
EDEAGOS = PRANCHA / "edeagos"

# ── Mapeamento espécie → prancha fotográfica ───────────────────────────────────
# Pranchas temporariamente removidas — sendo refeitas
FOTOS_ESPECIES: dict = {}

# ── Configuração da página ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chave de identificação ilustrada de drosofilídeos com ocorrência na região Neotropical",
    page_icon=None,
    layout="wide",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Expander "Pranchas crípticas" — fonte 2x maior */
[data-testid="stExpander"] summary p {
    font-size: 2.0rem !important;
    font-weight: 700 !important;
}

/* Borda adaptável nos campos de entrada */
[data-baseweb="select"] > div:first-child {
    border: 1.5px solid rgba(128,128,128,0.55) !important;
    border-radius: 0.4rem !important;
}
[data-baseweb="input"] {
    border: 1.5px solid rgba(128,128,128,0.55) !important;
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

/* Selectbox — container fechado */
[data-baseweb="select"] > div:first-child {
    min-height: 3.5rem !important;
    align-items: center !important;
    padding: 0.4rem 0.8rem !important;
    box-sizing: border-box !important;
    margin-top: 0 !important;
}

/* Input — margem top igual ao selectbox */
[data-baseweb="input"] > div {
    margin-top: 0.5rem !important;
}

/* Espaçamento entre campos */
[data-testid="stSelectbox"],
[data-testid="stTextInput"] {
    margin-bottom: 1.8rem !important;
}

/* Selectbox — todo texto interno */
[data-baseweb="select"],
[data-baseweb="select"] *,
[data-baseweb="select"] div,
[data-baseweb="select"] span,
[data-baseweb="select"] p {
    font-size: 1.50rem !important;
    line-height: 2.2rem !important;
}

/* Input (I. costal) */
[data-baseweb="input"] {
    min-height: 3.5rem !important;
    align-items: center !important;
    margin-top: 0 !important;
    box-sizing: border-box !important;
}
[data-baseweb="input"] input {
    font-size: 1.50rem !important;
    line-height: 2.2rem !important;
    padding: 0.4rem 0.8rem !important;
}

/* Opções do menu aberto */
[data-baseweb="menu"] li,
[data-baseweb="menu"] [role="option"],
[data-baseweb="popover"] li,
[data-baseweb="popover"] [role="option"],
[data-baseweb="menu"] *,
[data-baseweb="popover"] * {
    font-size: 1.50rem !important;
    line-height: 2.2rem !important;
    padding-top: 0.65rem !important;
    padding-bottom: 0.65rem !important;
}

/* Botão principal */
button[kind="primary"] {
    background: linear-gradient(135deg, #1b6f3c 0%, #28a056 100%) !important;
    border: none !important;
    font-weight: 800 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    box-shadow: 0 6px 20px rgba(27,111,60,0.45) !important;
    font-size: 1.75rem !important;
    line-height: 2.5rem !important;
    padding: 1.4rem 3rem !important;
    min-height: 6rem !important;
    border-radius: 0.75rem !important;
    width: 100% !important;
    transition: box-shadow 0.2s, transform 0.15s !important;
}
button[kind="primary"]:hover {
    box-shadow: 0 10px 30px rgba(27,111,60,0.55) !important;
    transform: translateY(-2px) !important;
}
button[kind="primary"] p,
button[kind="primary"] span,
button[kind="primary"] div {
    font-size: 1.75rem !important;
    font-weight: 800 !important;
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
            col_l, col_c, col_r = st.columns([0.2, 0.6, 0.2])
            with col_c:
                zoom = st.session_state.get(f"zoom_{caracteristica}_{label}", 75)
                st.image(str(img_path), width=int(480 * zoom / 100))

            st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)
            col_zl, col_zm, col_zr = st.columns([0.2, 0.6, 0.2])
            with col_zm:
                st.slider(
                    "Zoom",
                    min_value=25, max_value=150, value=75, step=25,
                    format="%d%%",
                    key=f"zoom_{caracteristica}_{label}",
                )


# ── Modal placeholder (sem imagem ainda) ──────────────────────────────────────

@st.dialog("Referência Fotográfica", width="large")
def mostrar_placeholder(caracteristica: str) -> None:
    st.markdown(
        f"<h4 style='text-align:center; color:inherit; opacity:0.85; margin-bottom:1.2rem;'>"
        f"{caracteristica}</h4>",
        unsafe_allow_html=True,
    )
    st.info("🔬 Imagem de referência em breve.", icon=None)


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
    <h1 style="margin:0 0 0.35rem; font-size:3.0rem; font-weight:700;">
        Chave de identificação ilustrada de drosofilídeos com ocorrência na região Neotropical
    </h1>
    <p style="margin:0.6rem 0 0; font-size:1.56rem; opacity:0.55;">versão {VERSAO}</p>
</div>
""", unsafe_allow_html=True)

# ── Seção de entrada ───────────────────────────────────────────────────────────
st.markdown("""
<div style="background:var(--secondary-background-color); border-radius:0.75rem;
            padding:1.2rem 1.8rem 0.2rem;
            box-shadow:0 1px 5px rgba(0,0,0,0.07); margin-bottom:1rem;">
    <h3 style="margin:0 0 0.15rem; color:inherit; font-size:2.0rem; font-weight:600;">
        Caracteres observados
    </h3>
    <p style="margin:0 0 0.8rem; color:inherit; opacity:0.65; font-size:1.75rem;">
        Selecione as características do espécime. Clique em <strong>ⓘ</strong>
        ao lado do nome para ver a referência fotográfica.
    </p>
</div>
""", unsafe_allow_html=True)

entrada_usuario = {}
cols = st.columns(3, gap="medium")

for i, c in enumerate(caracteristicas):
    with cols[i % 3]:
        tem_foto        = c.lower() in FOTOS_REFERENCIA
        tem_placeholder = c.lower() in PLACEHOLDERS_REFERENCIA
        label_display   = c.capitalize() if c.lower() == "coloração escura últimos tergitos (macho)" else c

        # ── Bloco label + ⓘ na mesma linha ──
        if tem_foto or tem_placeholder:
            col_label, col_btn = st.columns([0.88, 0.12])
            with col_label:
                st.markdown(
                    f"<div style='min-height:4.5rem; display:flex; align-items:flex-end; padding-bottom:0.15rem;'>"
                    f"<span style='font-size:2.0rem; font-weight:600; color:inherit; "
                    f"line-height:1.3;'>{label_display}</span></div>",
                    unsafe_allow_html=True,
                )
            with col_btn:
                st.markdown("<div style='min-height:4.5rem; display:flex; align-items:flex-end; padding-bottom:0.3rem;'>", unsafe_allow_html=True)
                if st.button("ⓘ", key=f"info_{c}", help="Ver referência fotográfica"):
                    if tem_foto:
                        mostrar_referencia(c)
                    else:
                        mostrar_placeholder(c)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div style='min-height:4.5rem; display:flex; align-items:flex-end; padding-bottom:0.15rem;'>"
                f"<span style='font-size:2.0rem; font-weight:600; color:inherit; "
                f"line-height:1.3;'>{label_display}</span></div>",
                unsafe_allow_html=True,
            )

        # ── Campo (dropdown ou input) ──
        if c.lower() == "i. costal":
            valor = st.text_input(
                c, placeholder="Digite o valor numérico",
                label_visibility="collapsed", key=f"input_{c}",
            )
        else:
            opcoes = df[c].dropna().unique()
            if c.lower() == "coloração":
                opcoes = [o for o in opcoes if o.lower() != "acastanhada"]
            valor = st.selectbox(
                c, ["Desconhecido"] + list(opcoes),
                label_visibility="collapsed", key=c,
            )

        entrada_usuario[c] = valor

st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)

# ── Botão de identificação ─────────────────────────────────────────────────────
_, col_btn, _ = st.columns([0.25, 0.50, 0.25])
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
        <p style="margin:0; font-size:4.65rem; font-weight:700; font-style:italic;">
            {nome_com_grupo(nome_especie)}
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
            f"Prancha fotográfica — <em>{nome_com_grupo(nome_especie)}</em></h4>",
            unsafe_allow_html=True,
        )
        col_foto, col_info = st.columns([0.55, 0.45])
        with col_foto:
            st.image(str(foto_esp), caption=nome_especie, use_container_width=True)
        with col_info:
            st.markdown(f"""
            <div style="background:var(--secondary-background-color); border-left:4px solid #2d6aad;
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

    # ── Calcula top5 e espécies crípticas ────────────────────────────────────
    top5 = resultados.head(5).copy()
    top5["Similaridade (%)"] = (top5["Similaridade"] * 100).round(1)

    def badge_criptica(nome: str) -> str:
        g = grupo_criptico(nome)
        if g:
            return (
                f" <span title='\"Espécie críptica\" — grupo {g}' "
                f"style='color:#e67e22; font-weight:900; font-size:1.3rem; "
                f"cursor:help;'>!</span>"
            )
        return ""

    cripticas_top5 = [
        (r["Espécie"], grupo_criptico(r["Espécie"]))
        for _, r in top5.iterrows()
        if grupo_criptico(r["Espécie"])
    ]

    # ── Alerta espécies crípticas (acima da tabela) ───────────────────────────
    if cripticas_top5:
        grupos_detectados = sorted({g for _, g in cripticas_top5})
        nomes_detectados  = ", ".join(f"*{n}*" for n, _ in cripticas_top5)
        st.markdown(f"""
        <div style="background:#fff3cd; border-left:5px solid #e67e22;
                    padding:1rem 1.4rem; border-radius:0 0.6rem 0.6rem 0;
                    margin:1rem 0;">
            <p style="margin:0 0 0.3rem; font-size:1.3rem; font-weight:700; color:#7d4e00;">
                ! Atenção — "Espécies crípticas" detectadas nas sugestões
            </p>
            <p style="margin:0; font-size:1.1rem; color:#5a3800;">
                {nomes_detectados} pertencem ao(s) grupo(s)
                <strong>{', '.join(grupos_detectados)}</strong>,
                considerados grupos de "espécies crípticas".
                A identificação definitiva <strong>requer análise do edeago</strong>
                (morfologia interna da terminália masculina),
                pois os caracteres externos não permitem distingui-las com segurança.
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Características diagnósticas dos grupos de espécies crípticas com maior nível de similaridade"):
            st.markdown("""
**O que são "espécies crípticas"?**
São espécies reprodutivamente isoladas que compartilham morfologia externa muito semelhante.
Nos grupos *melanogaster*, *repleta*, *willistoni* e *saltans*, a distinção
segura só é possível pela análise do **edeago** (órgão copulador masculino),
pois os caracteres externos não permitem distingui-las com segurança.
            """)
            st.divider()

            cols_pr = st.columns(len(cripticas_top5))
            for col, (nome_crit, grupo_crit) in zip(cols_pr, cripticas_top5):
                with col:
                    st.markdown(
                        f"<p style='text-align:center; font-style:italic; "
                        f"font-size:1.1rem; font-weight:600; margin-bottom:0.3rem;'>"
                        f"{nome_crit}<br>"
                        f"<span style='color:#e67e22; font-size:0.85em; font-style:normal;'>"
                        f"grupo {grupo_crit}</span></p>",
                        unsafe_allow_html=True,
                    )
                    img_pr = FOTOS_ESPECIES.get(nome_crit.lower().strip())
                    if img_pr and img_pr.exists():
                        st.image(str(img_pr), caption=nome_crit,
                                 use_container_width=True)
                    else:
                        st.info("Prancha não disponível.")

    # ── Top 5 ─────────────────────────────────────────────────────────────────
    st.markdown(
        "<h2 style='font-size:2.2rem; font-weight:700; margin:1.2rem 0 0.6rem;'>"
        "Espécies com maior similaridade</h2>",
        unsafe_allow_html=True,
    )
    rows_top5 = "".join(
        f"<tr>"
        f"<td style='font-size:1.5rem; padding:0.55rem 1rem; font-style:italic;'>"
        f"{nome_com_grupo(r['Espécie'])}</td>"
        f"<td style='font-size:1.5rem; padding:0.55rem 1rem; text-align:right;'>{r['Similaridade (%)']:.1f}%</td>"
        f"</tr>"
        for _, r in top5.iterrows()
    )
    st.markdown(
        f"<table style='width:100%; border-collapse:collapse; margin-bottom:0.5rem;'>"
        f"<thead><tr>"
        f"<th style='font-size:1.2rem; padding:0.4rem 1rem; text-align:left; border-bottom:2px solid #aaa;'>Espécie</th>"
        f"<th style='font-size:1.2rem; padding:0.4rem 1rem; text-align:right; border-bottom:2px solid #aaa;'>Similaridade (%)</th>"
        f"</tr></thead><tbody>{rows_top5}</tbody></table>",
        unsafe_allow_html=True,
    )

    # Ranking completo expansível
    with st.expander("Ver ranking completo"):
        ranking = resultados.copy()
        ranking["Similaridade (%)"] = (ranking["Similaridade"] * 100).round(1)
        rows_rank = "".join(
            f"<tr>"
            f"<td style='font-size:1.4rem; padding:0.45rem 1rem; font-style:italic;'>"
            f"{nome_com_grupo(r['Espécie'])}</td>"
            f"<td style='font-size:1.4rem; padding:0.45rem 1rem; text-align:right;'>{r['Similaridade (%)']:.1f}%</td>"
            f"</tr>"
            for _, r in ranking.iterrows()
        )
        st.markdown(
            f"<table style='width:100%; border-collapse:collapse;'>"
            f"<thead><tr>"
            f"<th style='font-size:1.2rem; padding:0.4rem 1rem; text-align:left; border-bottom:2px solid #aaa;'>Espécie</th>"
            f"<th style='font-size:1.2rem; padding:0.4rem 1rem; text-align:right; border-bottom:2px solid #aaa;'>Similaridade (%)</th>"
            f"</tr></thead><tbody>{rows_rank}</tbody></table>",
            unsafe_allow_html=True,
        )

    # Gráfico
    st.markdown(
        "<h2 style='font-size:2.2rem; font-weight:700; margin:1.2rem 0 0.6rem;'>"
        "Gráfico de similaridade</h2>",
        unsafe_allow_html=True,
    )
    import altair as alt
    chart = alt.Chart(resultados).mark_bar().encode(
        x=alt.X("Espécie:N", sort="-y", axis=alt.Axis(labelFontSize=16, titleFontSize=16, labelAngle=-45)),
        y=alt.Y("Similaridade:Q", axis=alt.Axis(labelFontSize=16, titleFontSize=16)),
    )
    st.altair_chart(chart, use_container_width=True)
