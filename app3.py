import streamlit as st
import pandas as pd
import numpy as np

# Configura a página do Streamlit para usar a largura total da tela
st.set_page_config(layout="wide")

# Função decorada com cache para evitar recarregar o arquivo CSV a cada interação na tela
@st.cache_data
def carregar_dados():
    # Carrega a base de dados contendo a chave de identificação taxonômica
    df = pd.read_csv("chave.csv")
    return df

# Carrega os dados para o DataFrame
df = carregar_dados()

# Define qual é a coluna das espécies (primeira coluna do arquivo)
coluna_especie = df.columns[0]

# Define a lista de características morfológicas (da segunda coluna em diante)
caracteristicas = df.columns[1:]

# Define o título principal da aplicação web
st.title("Identificador de Espécies de drosofílideos")

# Exibe uma breve descrição do sistema
st.write(
"""
Sistema digital de identificação taxonômica baseado em
características morfológicas.
"""
)

# Mensagens/Alertas de teste na interface gráfica
st.warning("Teste")
st.success("Teste")
st.info("Teste")

# Linha divisória visual
st.divider()

# Subtítulo da seção de entrada de dados
st.subheader("Selecione ou digite as características observadas")

# Dicionário para armazenar as características informadas pelo usuário
entrada_usuario = {}

# Define o número de colunas para organizar os campos na tela
num_colunas = 3
cols = st.columns(num_colunas)

# Loop para renderizar dinamicamente os campos de entrada para cada característica
for i, c in enumerate(caracteristicas):
    with cols[i % num_colunas]:
        # Se a característica for o índice costal ("i. costal"), exibe um campo de texto livre
        if c.lower() == "i. costal":
            valor = st.text_input(
                c,
                placeholder="Digite o valor observado"
            )
        # Para as demais características, exibe uma caixa de seleção (selectbox) com valores únicos da tabela
        else:
            opcoes = df[c].dropna().unique()
            valor = st.selectbox(
                c,
                ["Desconhecido"] + list(opcoes),
                key=c
            )
        # Guarda a opção selecionada no dicionário de entradas do usuário
        entrada_usuario[c] = valor

# Função para calcular a similaridade morfológica entre uma espécie da base e a entrada do usuário
def calcular_similaridade(linha, entrada):
    total = 0
    match = 0
    for c in caracteristicas:
        valor_usuario = str(entrada[c]).strip().lower()
        # Desconsidera características não informadas ou marcadas como "Desconhecido"
        if valor_usuario == "" or valor_usuario == "desconhecido":
            continue
        total += 1
        valor_base = str(linha[c]).strip().lower()
        # Verifica se o valor informado está contido no valor cadastrado na base de dados
        if valor_usuario in valor_base:
            match += 1
    # Evita divisão por zero se o usuário não preencher nenhuma característica
    if total == 0:
        return 0
    return match / total

# Linha divisória visual
st.divider()

# Botão para disparar o processo de identificação taxonômica
if st.button("Identificar Espécie"):
    resultados = []
    # Itera sobre cada linha da tabela de espécies para calcular a similaridade
    for i, linha in df.iterrows():
        score = calcular_similaridade(linha, entrada_usuario)
        resultados.append({
            "Espécie": linha[coluna_especie],
            "Similaridade": score
        })
    
    # Converte os resultados obtidos em um DataFrame do Pandas
    resultados = pd.DataFrame(resultados)
    # Ordena os resultados da maior similaridade para a menor
    resultados = resultados.sort_values(
        "Similaridade",
        ascending=False
    )
    
    # Obtém a espécie com maior pontuação de similaridade
    melhor = resultados.iloc[0]
    
    # Se a maior similaridade for zero, informa que os dados são insuficientes
    if melhor["Similaridade"] == 0:
        st.warning("Dados insuficientes para a classificação.")
        st.stop()
    else:
        # Exibe a espécie mais provável identificada pelo sistema
        st.subheader("Espécie mais provável")
        st.success(
            f"{melhor['Espécie']} "
            f"(similaridade {round(melhor['Similaridade']*100,1)}%)"
        )
        
        # Exibe as top 5 espécies com maior similaridade
        st.subheader("Espécies semelhantes")
        top5 = resultados.head(5).copy()
        top5["Similaridade (%)"] = top5["Similaridade"] * 100
        st.dataframe(
            top5[["Espécie", "Similaridade (%)"]],
            use_container_width=True
        )
        
        # Renderiza um gráfico de barras com as similaridades das espécies
        st.subheader("Gráfico de similaridade")
        st.bar_chart(
            resultados.set_index("Espécie")["Similaridade"]
        )
        
    # Reapresentação e detalhamento completo dos resultados na interface gráfica
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
