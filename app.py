
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard de Vendas por Empresa", layout="wide")
st.title("📈 Dashboard de Vendas Dinâmico por Empresa")

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
    st.warning(f"O arquivo '{arquivo_csv}' não foi encontrado. Por favor, envie o CSV correto para esta empresa.")
    st.stop()

# === Carregar os dados ===
df = pd.read_csv(arquivo_csv)

# === Validação básica ===
colunas_esperadas = {'Razao Social', 'Descricao', 'Data', 'vendas'}
if not colunas_esperadas.issubset(df.columns):
    st.error(f"O arquivo '{arquivo_csv}' está incompleto. Esperado: {colunas_esperadas}")
    st.stop()

# Padronizar nomes
df['Data'] = pd.to_datetime(df['Data'])

# Menu lateral
aba = st.sidebar.radio("Escolha a visualização:", [
    "📊 Previsão por Produto", "🏆 Ranking de Vendas", "📌 Produtos Recomendados",
    "📉 Análise de Churn", "🔁 Previsão de Recompra", "📦 Pedido Sugerido"
])

# === Aba Pedido Sugerido com Filtros e DRE ===
if aba == "📦 Pedido Sugerido":
    st.subheader("📦 Pedido Sugerido por Cliente e Produto + DRE")
    df_sorted = df.sort_values(['Razao Social', 'Descricao', 'Data'])
    df_sorted['Dias_entre_compras'] = df_sorted.groupby(['Razao Social', 'Descricao'])['Data'].diff().dt.days

    resumo = df_sorted.groupby(['Razao Social', 'Descricao']).agg({
        'Data': 'max',
        'Dias_entre_compras': 'mean',
        'vendas': 'mean',
        'CUSTO': 'mean' if 'CUSTO' in df.columns else 'sum',
        'IMPOSTO': 'mean' if 'IMPOSTO' in df.columns else 'sum'
    }).dropna().reset_index()

    resumo = resumo.rename(columns={
        'Data': 'Ultima_Compra',
        'Dias_entre_compras': 'Média_Dias_Entre_Compras',
        'vendas': 'Média_Quantidade',
        'CUSTO': 'Custo_Médio',
        'IMPOSTO': 'Imposto_Médio'
    })

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
    st.dataframe(resumo_filtrado[colunas_exibir].sort_values(by='Pedido_Sugerido', ascending=False))

    st.markdown("### 📊 Totais Consolidados")
    totais = resumo_filtrado[['Receita', 'Custo_Total', 'Imposto_Total', 'Margem_Contribuicao']].sum()
    st.write(pd.DataFrame(totais).rename(columns={0: 'Total'}))

st.caption("Dashboard completo com previsão, churn, recompra, recomendação e pedidos sugeridos com DRE estimado por produto.")
