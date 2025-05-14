
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# URL do arquivo CSV no Google Drive (formato direto de download)
url = "https://drive.google.com/uc?export=download&id=1aB1hZfJ04pYYFAQ62fy7O_FA-UxfkGr8"

# Carregar os dados
df = pd.read_csv(url)

st.set_page_config(page_title="Previsão de Vendas por IA", layout="wide")
st.title("📊 Dashboard de Previsão de Vendas por Cliente e Produto")

# Filtros
clientes = df['cliente_id'].unique()
produtos = df['produto_id'].unique()

cliente_selecionado = st.sidebar.selectbox("Selecione o Cliente", sorted(clientes))
produto_selecionado = st.sidebar.selectbox("Selecione o Produto", sorted(produtos))

# Filtrar os dados
filtro = (df['cliente_id'] == cliente_selecionado) & (df['produto_id'] == produto_selecionado)
df_filtrado = df[filtro]

# Exibir tabela
st.subheader("Previsão de Vendas para os Próximos 30 Dias")
st.dataframe(df_filtrado[['Data', 'vendas_previstas']].reset_index(drop=True))

# Gráfico
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(pd.to_datetime(df_filtrado['Data']), df_filtrado['vendas_previstas'], marker='o')
ax.set_title("Previsão de Vendas Diárias")
ax.set_xlabel("Data")
ax.set_ylabel("Vendas Previstas (R$)")
ax.grid(True)
st.pyplot(fig)

st.caption("Modelo preditivo treinado com Random Forest usando dados reais da empresa")
