import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from datetime import datetime

# === Seleção da empresa ===
st.sidebar.header("🏢 Empresa")
empresas = {
    "Brasforma": "empresa_brasforma.csv",
    "Fort Solutions": "empresa_fortsolutions.csv"
}
empresa_escolhida = st.sidebar.selectbox("Selecione a empresa:", list(empresas.keys()))
arquivo_csv = empresas[empresa_escolhida]

# === Verificar e carregar o CSV correspondente ===
if not os.path.exists(arquivo_csv):
    st.error(f"Arquivo '{arquivo_csv}' não encontrado para a empresa selecionada.")
    st.stop()

# Carregar os dados da empresa
try:
    df = pd.read_csv(arquivo_csv)
except Exception as e:
    st.error(f"Erro ao carregar o arquivo '{arquivo_csv}': {e}")
    st.stop()

# Validar colunas obrigatórias
colunas_necessarias = {'Razao Social', 'Item', 'Data', 'vendas'}
if not colunas_necessarias.issubset(df.columns):
    st.error("O arquivo CSV deve conter as colunas: Razao Social, Item, Data, vendas")
    st.stop()

# Ajustar nomes esperados
st.set_page_config(page_title="Dashboard de Vendas por Empresa", layout="wide")
st.title(f"📈 Dashboard de Vendas - {empresa_escolhida}")

# Conversão de data e renomeação para manter compatibilidade
df['Data'] = pd.to_datetime(df['Data'])
df = df.rename(columns={'Item': 'Descricao'})

# Menu principal
aba = st.sidebar.radio("Escolha a visualização:", [
    "📊 Previsão por Produto", "🏆 Ranking de Vendas", "📌 Produtos Recomendados", "📉 Análise de Churn", "🔁 Previsão de Recompra"])

if aba == "📊 Previsão por Produto":
    st.sidebar.header("🔍 Filtros")
    clientes = sorted(df['Razao Social'].dropna().unique())
    cliente_opcao = st.sidebar.selectbox("Selecione a Razão Social", clientes)

    produtos_cliente = sorted(df[df['Razao Social'] == cliente_opcao]['Descricao'].dropna().unique())
    produto_opcao = st.sidebar.selectbox("Selecione o Produto", produtos_cliente)

    datas_disponiveis = df['Data'].sort_values()
    data_inicio = st.sidebar.date_input("Data inicial", datas_disponiveis.min())
    data_fim = st.sidebar.date_input("Data final", datas_disponiveis.max())

    filtro = (
        (df['Razao Social'] == cliente_opcao) &
        (df['Descricao'] == produto_opcao) &
        (df['Data'] >= pd.to_datetime(data_inicio)) &
        (df['Data'] <= pd.to_datetime(data_fim))
    )

    df_filtrado = df[filtro].sort_values('Data')
    df_filtrado['média_móvel'] = df_filtrado['vendas'].rolling(window=7).mean()

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("📊 Dados Filtrados")
        st.dataframe(df_filtrado[['Data', 'vendas', 'média_móvel']].reset_index(drop=True))
    with col2:
        st.subheader("📉 Gráfico de Vendas")
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(df_filtrado['Data'], df_filtrado['vendas'], label="Vendas", marker='o')
        ax.plot(df_filtrado['Data'], df_filtrado['média_móvel'], label="Média Móvel (7 dias)", linestyle='--')
        ax.set_title("Evolução de Vendas")
        ax.set_xlabel("Data")
        ax.set_ylabel("Vendas (R$)")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

elif aba == "🏆 Ranking de Vendas":
    st.subheader("🏆 Ranking de Vendas por Cliente e Produto")
    ranking = df.groupby(['Razao Social', 'Descricao'])['vendas'].sum().reset_index()
    ranking = ranking.sort_values(by='vendas', ascending=False)
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

elif aba == "📉 Análise de Churn":
    st.subheader("📉 Clientes Inativos (Risco de Churn)")
    hoje = pd.to_datetime(datetime.today())
    ultima_compra = df.groupby('Razao Social')['Data'].max().reset_index()
    ultima_compra['Dias_sem_compra'] = (hoje - ultima_compra['Data']).dt.days
    dias_corte = st.slider("Clientes inativos há pelo menos (dias):", 15, 120, 30)
    churn = ultima_compra[ultima_compra['Dias_sem_compra'] >= dias_corte].sort_values(by='Dias_sem_compra', ascending=False)
    st.dataframe(churn.reset_index(drop=True))

elif aba == "🔁 Previsão de Recompra":
    st.subheader("🔁 Previsão de Recompra por Cliente")
    df_frequencia = df.sort_values(['Razao Social', 'Data'])
    df_frequencia['Dias_entre_compras'] = df_frequencia.groupby('Razao Social')['Data'].diff().dt.days
    media_dias = df_frequencia.groupby('Razao Social')['Dias_entre_compras'].mean().dropna().reset_index()
    ultima_data = df.groupby('Razao Social')['Data'].max().reset_index()
    previsao = pd.merge(media_dias, ultima_data, on='Razao Social')
    previsao['Proxima_Compra_Estimada'] = previsao['Data'] + pd.to_timedelta(previsao['Dias_entre_compras'], unit='D')
    st.dataframe(previsao[['Razao Social', 'Dias_entre_compras', 'Proxima_Compra_Estimada']].sort_values(by='Proxima_Compra_Estimada'))

st.caption("Dashboard dinâmico com seleção de empresa, análise de vendas, churn, recompra e recomendação de produtos.")
