import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

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

# Menu principal
aba = st.sidebar.radio("Escolha a visualização:", [
    "📊 Previsão por Produto", "🏆 Ranking de Vendas", "📌 Produtos Recomendados"])

# Converter datas
df['Data'] = pd.to_datetime(df['Data'])

if aba == "📊 Previsão por Produto":
    st.sidebar.header("🔍 Filtros")
    clientes = sorted(df['Razao Social'].dropna().unique())
    cliente_opcao = st.sidebar.selectbox("Selecione a Razão Social", clientes)

    produtos_cliente = sorted(df[df['Razao Social'] == cliente_opcao]['Descricao'].dropna().unique())
    produto_opcao = st.sidebar.selectbox("Selecione o Produto", produtos_cliente)

    familias = sorted(df['Familia'].dropna().unique()) if 'Familia' in df.columns else []
    if familias:
        familia_opcao = st.sidebar.selectbox("Selecione a Família", ["Todas"] + familias)
    else:
        familia_opcao = "Todas"

    datas_disponiveis = df['Data'].sort_values()
    data_inicio = st.sidebar.date_input("Data inicial", datas_disponiveis.min())
    data_fim = st.sidebar.date_input("Data final", datas_disponiveis.max())

    filtro = (
        (df['Razao Social'] == cliente_opcao) &
        (df['Descricao'] == produto_opcao) &
        (df['Data'] >= pd.to_datetime(data_inicio)) &
        (df['Data'] <= pd.to_datetime(data_fim))
    )
    if familia_opcao != "Todas":
        filtro &= (df['Familia'] == familia_opcao)

    df_filtrado = df[filtro].sort_values('Data')
    df_filtrado['média_móvel'] = df_filtrado['vendas_previstas'].rolling(window=7).mean()

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

elif aba == "🏆 Ranking de Vendas":
    st.subheader("🏆 Ranking de Vendas Previstas por Cliente e Produto")
    ranking = df.groupby(['Razao Social', 'Descricao'])['vendas_previstas'].sum().reset_index()
    ranking = ranking.sort_values(by='vendas_previstas', ascending=False)
    st.dataframe(ranking.head(20))

elif aba == "📌 Produtos Recomendados":
    st.subheader("📌 Recomendação de Produtos por Perfil de Cliente")
    df_bin = df.copy()
    df_bin['comprou'] = 1
    matriz = df_bin.groupby(['Razao Social', 'Descricao'])['comprou'].sum().unstack().fillna(0)
    matriz_binaria = matriz.applymap(lambda x: 1 if x > 0 else 0)

    cliente_exemplo = st.selectbox("Selecione um cliente para recomendação:", matriz_binaria.index)

    similaridade = pd.DataFrame(cosine_similarity(matriz_binaria),
                                index=matriz_binaria.index,
                                columns=matriz_binaria.index)
    similares = similaridade[cliente_exemplo].sort_values(ascending=False).iloc[1:6]
    produtos_cliente = matriz_binaria.loc[cliente_exemplo]
    recomendados = []

    for cliente_similar in similares.index:
        produtos_similar = matriz_binaria.loc[cliente_similar]
        novos = (produtos_similar == 1) & (produtos_cliente == 0)
        recomendados.extend(produtos_similar[novos].index.tolist())

    ranking_recomendados = Counter(recomendados).most_common()
    df_recomendados = pd.DataFrame(ranking_recomendados, columns=['Produto', 'Score'])

    st.write(f"Produtos recomendados para **{cliente_exemplo}** com base em perfil de compra:")
    st.dataframe(df_recomendados.head(10))

st.caption("Modelo preditivo treinado com Random Forest e recomendações baseadas em similaridade de perfil.")
