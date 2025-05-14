import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# Verificar se o arquivo existe
file_path = "previsoes_com_nomes.csv"
if not os.path.exists(file_path):
    st.error("Arquivo 'previsoes_com_nomes.csv' não encontrado no diretório do app.")
    st.stop()

# Carregar os dados
df = pd.read_csv(file_path)

# Validar colunas obrigatórias
colunas_necessarias = {'Razao Social', 'Descricao', 'Data', 'vendas_previstas'}
if not colunas_necessarias.issubset(df.columns):
    st.error("O arquivo CSV deve conter as colunas: Razao Social, Descricao, Data, vendas_previstas")
    st.stop()

# Configurações da página
st.set_page_config(page_title="Previsão de Vendas por IA", layout="wide")
st.title("📈 Dashboard de Previsão de Vendas por Cliente e Produto")

# Sidebar com filtros
st.sidebar.header("🔍 Filtros")

df['Data'] = pd.to_datetime(df['Data'])
clientes = sorted(df['Razao Social'].dropna().unique())
produtos = sorted(df['Descricao'].dropna().unique())
familias = sorted(df['Familia'].dropna().unique()) if 'Familia' in df.columns else []

cliente_opcao = st.sidebar.selectbox("Selecione a Razão Social", clientes)
produto_opcao = st.sidebar.selectbox("Selecione o Produto", produtos)
if familias:
    familia_opcao = st.sidebar.selectbox("Selecione a Família", ["Todas"] + familias)
else:
    familia_opcao = "Todas"

datas_disponiveis = df['Data'].sort_values()
data_inicio = st.sidebar.date_input("Data inicial", datas_disponiveis.min())
data_fim = st.sidebar.date_input("Data final", datas_disponiveis.max())

# Aplicar filtros
filtro = (
    (df['Razao Social'] == cliente_opcao) &
    (df['Descricao'] == produto_opcao) &
    (df['Data'] >= pd.to_datetime(data_inicio)) &
    (df['Data'] <= pd.to_datetime(data_fim))
)
if familia_opcao != "Todas":
    filtro &= (df['Familia'] == familia_opcao)

df_filtrado = df[filtro]

# Calcular média móvel (7 dias)
df_filtrado = df_filtrado.sort_values('Data')
df_filtrado['média_móvel'] = df_filtrado['vendas_previstas'].rolling(window=7).mean()

# Layout principal
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 Dados Filtrados")
    st.dataframe(df_filtrado[['Data', 'vendas_previstas', 'média_móvel']].reset_index(drop=True))

with col2:
    st.subheader("📉 Gráfico de Previsões")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df_filtrado['Data'], df_filtrado['vendas_previstas'], label="Vendas Previstas", marker='o')
    ax.plot(df_filtrado['Data'], df_filtrado['média_móvel'], label="Média Móvel (7 dias)", linestyle='--')
    ax.set_title("Previsão de Vendas Diárias")
    ax.set_xlabel("Data")
    ax.set_ylabel("Vendas Previstas (R$)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

# Aba de Ranking
st.subheader("🏆 Ranking de Vendas Previstas por Cliente e Produto")
ranking = df.groupby(['Razao Social', 'Descricao'])['vendas_previstas'].sum().reset_index()
ranking = ranking.sort_values(by='vendas_previstas', ascending=False)
st.dataframe(ranking.head(20))

st.caption("Modelo preditivo treinado com Random Forest usando dados reais da empresa")
