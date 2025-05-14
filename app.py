
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Carregar o CSV com nomes reais de cliente e produto
df = pd.read_csv("previsoes_com_nomes.csv")

st.set_page_config(page_title="Previsão de Vendas por IA", layout="wide")
st.title("📊 Dashboard de Previsão de Vendas por Cliente e Produto")

# Sidebar com filtros por nome e período
st.sidebar.header("Filtros")

clientes = sorted(df['Razao Social'].dropna().unique())
produtos = sorted(df['Descricao'].dropna().unique())

cliente_opcao = st.sidebar.selectbox("Selecione a Razão Social", clientes)
produto_opcao = st.sidebar.selectbox("Selecione o Produto", produtos)

df['Data'] = pd.to_datetime(df['Data'])
datas_disponiveis = df['Data'].sort_values()
data_inicio = st.sidebar.date_input("Data inicial", datas_disponiveis.min())
data_fim = st.sidebar.date_input("Data final", datas_disponiveis.max())

# Filtrar os dados
df_filtrado = df[(df['Razao Social'] == cliente_opcao) &
                 (df['Descricao'] == produto_opcao) &
                 (df['Data'] >= pd.to_datetime(data_inicio)) &
                 (df['Data'] <= pd.to_datetime(data_fim))]

# Exibir tabela
st.subheader("Previsão de Vendas Filtrada")
st.dataframe(df_filtrado[['Data', 'vendas_previstas']].reset_index(drop=True))

# Gráfico
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df_filtrado['Data'], df_filtrado['vendas_previstas'], marker='o')
ax.set_title("Previsão de Vendas Diárias")
ax.set_xlabel("Data")
ax.set_ylabel("Vendas Previstas (R$)")
ax.grid(True)
st.pyplot(fig)

# Aba de Ranking
st.subheader("🏆 Ranking de Vendas Previstas por Cliente e Produto")
ranking = df.groupby(['Razao Social', 'Descricao'])['vendas_previstas'].sum().reset_index()
ranking = ranking.sort_values(by='vendas_previstas', ascending=False)
st.dataframe(ranking.head(20))

st.caption("Modelo preditivo treinado com Random Forest usando dados reais da empresa")
