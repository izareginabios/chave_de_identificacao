# Identificador de Espécies de Drosofílideos

Sistema digital de identificação taxonômica baseado em características morfológicas,
desenvolvido com [Streamlit](https://streamlit.io/).

## Estrutura do projeto

```
drosophila/
├── app.py               # Ponto de entrada — interface Streamlit
├── src/
│   └── identificador.py # Lógica de carregamento de dados e cálculo de similaridade
├── data/
│   └── chave.csv        # Base de dados das espécies e suas características
├── requirements.txt     # Dependências do projeto
└── README.md
```

## Como executar

### 1. Crie e ative um ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Execute a aplicação

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no navegador em `http://localhost:8501`.

## Como usar

1. Selecione as características morfológicas observadas no espécime.
2. Para o **Índice Costal**, digite o valor numérico observado.
3. Clique em **Identificar Espécie**.
4. O sistema exibirá a espécie mais provável, as 5 mais semelhantes, o ranking completo e um gráfico de similaridade.
