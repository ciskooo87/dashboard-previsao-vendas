
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

if empresa_usuario == "ALL":
    empresa_escolhida = st.sidebar.selectbox("Selecione a empresa:", list(empresas.keys()))
else:
    empresa_escolhida = empresa_usuario
    st.sidebar.markdown(f"**Empresa:** {empresa_escolhida}")

arquivo_csv = empresas.get(empresa_escolhida)
if not arquivo_csv or not os.path.exists(arquivo_csv):
    st.error(f"O arquivo '{arquivo_csv}' não foi encontrado.")
    st.stop()

# === Carregamento e validação da base ===
df = pd.read_csv(arquivo_csv)
if 'Data' in df.columns:
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data'])

colunas_esperadas = {'Razao Social', 'Descricao', 'Data', 'vendas'}
if not colunas_esperadas.issubset(df.columns):
    st.error(f"Colunas ausentes: {colunas_esperadas - set(df.columns)}")
    st.stop()

# === Dashboard simplificado de confirmação ===
st.title(f"Dashboard de Vendas - {empresa_escolhida}")
st.write("Visualizando os 5 primeiros registros da base de dados:")
st.dataframe(df.head())
