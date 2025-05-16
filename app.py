
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard de Vendas por Empresa", layout="wide")
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

# Carregar CSV com conversão de data
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

if aba == "📦 Pedido Sugerido":
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

st.caption("Dashboard atualizado com tratamento seguro para datas e visualização dos dados da Padaria Cepam.")
