
import streamlit as st
st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

import pandas as pd
import os
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import matplotlib.pyplot as plt
import json

# === Login com JSON externo ===
with open("usuarios.json", "r") as f:
    usuarios = json.load(f)

st.sidebar.title("🔐 Login")
usuario = st.sidebar.text_input("Usuário")
senha = st.sidebar.text_input("Senha", type="password")

if usuario not in usuarios or senha != usuarios[usuario]["senha"]:
    st.sidebar.warning("Acesso restrito. Informe usuário e senha válidos.")
    st.stop()

empresa_usuario = usuarios[usuario]["empresa"]
st.sidebar.success(f"Bem-vindo, {usuario}")

# === Bases por empresa ===
empresas = {
    "Brasforma": "empresa_brasforma.csv",
    "Fort Solutions": "empresa_fortsolutions.csv",
    "Padaria Cepam": "empresa_cepam.csv"
}

if usuarios[usuario]["empresa"] == "ALL":
    empresa_escolhida = st.sidebar.selectbox("Selecione a empresa:", list(empresas.keys()))
else:
    empresa_escolhida = usuarios[usuario]["empresa"]
    st.sidebar.markdown(f"**Empresa:** {empresa_escolhida}")

arquivo_csv = empresas.get(empresa_escolhida)
if not arquivo_csv or not os.path.exists(arquivo_csv):
    st.error(f"O arquivo '{arquivo_csv}' não foi encontrado.")
    st.stop()

df = pd.read_csv(arquivo_csv)
if 'Data' in df.columns:
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data'])

colunas_esperadas = {'Razao Social', 'Descricao', 'Data', 'vendas'}
if not colunas_esperadas.issubset(df.columns):
    st.error(f"Colunas ausentes: {colunas_esperadas - set(df.columns)}")
    st.stop()



import streamlit as st
import pandas as pd
import os
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import matplotlib.pyplot as plt

st.title("📈 Dashboard de Vendas Dinâmico por Empresa")

st.sidebar.header("🏢 Empresa")
empresas = {
    "Brasforma": "empresa_brasforma.csv",
    "Fort Solutions": "empresa_fortsolutions.csv",
    "Padaria Cepam": "empresa_cepam.csv"
}
empresa_escolhida = st.sidebar.selectbox("Selecione a empresa:", list(empresas.keys()))
arquivo_csv = empresas[empresa_escolhida]

if not os.path.exists(arquivo_csv):
    st.warning(f"O arquivo '{arquivo_csv}' não foi encontrado.")
    st.stop()

df = pd.read_csv(arquivo_csv)
if 'Data' in df.columns:
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data'])

colunas_esperadas = {'Razao Social', 'Descricao', 'Data', 'vendas'}
if not colunas_esperadas.issubset(df.columns):
    st.error(f"Colunas ausentes: {colunas_esperadas - set(df.columns)}")
    st.stop()

aba = st.sidebar.radio("Escolha a visualização:", [
    "📊 Previsão por Produto", "🏆 Ranking de Vendas", "📌 Produtos Recomendados",
    "📉 Análise de Churn", "🔁 Previsão de Recompra", "📦 Pedido Sugerido"
])

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
        ax.set_ylabel("Vendas")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

elif aba == "🏆 Ranking de Vendas":
    st.subheader("🏆 Ranking de Vendas por Cliente e Produto")
    ranking = df.groupby(['Razao Social', 'Descricao'])['vendas'].sum().reset_index()
    ranking = ranking.sort_values(by='vendas', ascending=False)
    st.dataframe(ranking.head(50))

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

elif aba == "📦 Pedido Sugerido":
    st.subheader("📦 Pedido Sugerido por Cliente e Produto + DRE")
    df_sorted = df.sort_values(['Razao Social', 'Descricao', 'Data'])
    df_sorted['Dias_entre_compras'] = df_sorted.groupby(['Razao Social', 'Descricao'])['Data'].diff().dt.days

    agg_dict = {
        'Data': 'max',
        'Dias_entre_compras': 'mean',
        'vendas': 'mean'
    }
    if 'CUSTO' in df.columns:
        agg_dict['CUSTO'] = 'mean'
    if 'IMPOSTO' in df.columns:
        agg_dict['IMPOSTO'] = 'mean'

    resumo = df_sorted.groupby(['Razao Social', 'Descricao']).agg(agg_dict).dropna().reset_index()

    renomear = {
        'Data': 'Ultima_Compra',
        'Dias_entre_compras': 'Média_Dias_Entre_Compras',
        'vendas': 'Média_Quantidade'
    }
    if 'CUSTO' in resumo.columns:
        renomear['CUSTO'] = 'Custo_Médio'
    if 'IMPOSTO' in resumo.columns:
        renomear['IMPOSTO'] = 'Imposto_Médio'

    resumo = resumo.rename(columns=renomear)

    hoje = pd.to_datetime(datetime.today())
    resumo['Dias_desde_ultima'] = (hoje - resumo['Ultima_Compra']).dt.days
    resumo['Pedido_Sugerido'] = resumo.apply(
        lambda row: row['Média_Quantidade'] if row['Dias_desde_ultima'] >= row['Média_Dias_Entre_Compras'] else 0,
        axis=1
    )

    resumo['Receita'] = resumo['Pedido_Sugerido'] * resumo['Média_Quantidade']
    resumo['Custo_Total'] = resumo['Pedido_Sugerido'] * resumo.get('Custo_Médio', 0)
    resumo['Imposto_Total'] = resumo['Pedido_Sugerido'] * resumo.get('Imposto_Médio', 0)
    resumo['Margem_Contribuicao'] = resumo['Receita'] - resumo['Custo_Total'] - resumo['Imposto_Total']

    st.sidebar.header("🔍 Filtros de Pedido")
    clientes = ['Todos'] + sorted(resumo['Razao Social'].unique())
    produtos = ['Todos'] + sorted(resumo['Descricao'].unique())

    cliente_filtro = st.sidebar.selectbox("Filtrar por cliente:", clientes)
    produto_filtro = st.sidebar.selectbox("Filtrar por produto:", produtos)

    filtro = pd.Series(True, index=resumo.index)
    if cliente_filtro != 'Todos':
        filtro &= resumo['Razao Social'] == cliente_filtro
    if produto_filtro != 'Todos':
        filtro &= resumo['Descricao'] == produto_filtro

    resumo_filtrado = resumo[filtro]
    colunas_exibir = [
        'Razao Social', 'Descricao', 'Ultima_Compra', 'Média_Dias_Entre_Compras',
        'Média_Quantidade', 'Dias_desde_ultima', 'Pedido_Sugerido',
        'Receita', 'Custo_Total', 'Imposto_Total', 'Margem_Contribuicao'
    ]
    colunas_exibir = [c for c in colunas_exibir if c in resumo_filtrado.columns]

    st.dataframe(resumo_filtrado[colunas_exibir].sort_values(by='Pedido_Sugerido', ascending=False))

    st.markdown("### 📊 Totais Consolidados")
    totais = resumo_filtrado[[col for col in ['Receita', 'Custo_Total', 'Imposto_Total', 'Margem_Contribuicao'] if col in resumo_filtrado.columns]].sum()
    st.write(pd.DataFrame(totais).rename(columns={0: 'Total'}))

st.caption("Dashboard completo com todas as abas funcionando.")
