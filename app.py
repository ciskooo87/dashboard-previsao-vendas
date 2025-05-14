
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# URL do arquivo CSV no Google Drive (formato direto de download)
url = "https://drive.google.com/uc?export=download&id=1aB1hZfJ04pYYFAQ62fy7O_FA-UxfkGr8"

# Carregar os dados
df = pd.read_csv(url)

st.set_page_config(page_title="Previsão de Vendas por IA", layout="wide")
st.title("📊 Dashboard de Previsão de Vendas por Cliente e Produto")

# Sidebar com filtros por nome e período
st.sidebar.header("Filtros")

# Verifica se as colunas com nomes reais existem e usa elas
cliente_col = 'Razao Social' if 'Razao Social' in df.columns else 'cliente_id'
produto_col = 'Descricao' if 'Descricao' in df.columns else 'produto_id'

clientes = sorted(df[cliente_col].dropna().unique())
produtos = sorted(df[produto_col].dropna().unique())

cliente_opcao = st.sidebar.selectbox("Selecione a Razão Social", clientes)
produto_opcao = st.sidebar.selectbox("Selecione o Produto", produtos)

datas_disponiveis = pd.to_datetime(df['Data']).sort_values()
data_inicio = st.sidebar.date_input("Data inicial", datas_disponiveis.min())
data_fim = st.sidebar.date_input("Data final", datas_disponiveis.max())

# Filtrar os dados
df['Data'] = pd.to_datetime(df['Data'])
df_filtrado = df[(df[cliente_col] == cliente_opcao) &
                 (df[produto_col] == produto_opcao) &
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
ranking = df.groupby([cliente_col, produto_col])['vendas_previstas'].sum().reset_index()
ranking = ranking.sort_values(by='vendas_previstas', ascending=False)
st.dataframe(ranking.head(20))

st.caption("Modelo preditivo treinado com Random Forest usando dados reais da empresa")
