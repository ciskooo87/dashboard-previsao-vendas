
import streamlit as st
import pandas as pd
import os
import bcrypt
import json
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import matplotlib.pyplot as plt

st.set_page_config(page_title="ABIB Consultoria - Dashboard", layout="wide")

# Estilo customizado com nova paleta dinâmica e logo local
st.markdown("""
    <style>
        body {
            background-color: #fefefe;
        }
        .stApp {
            font-family: 'Segoe UI', sans-serif;
        }
        .stSidebar {
            background-color: #f0f0f5;
        }
        .stButton > button {
            background-color: #6A5ACD;
            color: white;
            border-radius: 6px;
            font-weight: bold;
        }
        .stButton > button:hover {
            background-color: #836FFF;
        }
        .stRadio > div, .stSelectbox > div {
            color: #4B0082;
        }
        .stMarkdown, .stHeader, .css-1v0mbdj {
            color: #4B0082;
        }
    </style>
""", unsafe_allow_html=True)

# Logo e título
st.image("logo_abib.png", width=180)
st.title("ABIB Consultoria | Dashboard de Vendas")

# Login com bcrypt
with open("usuarios.json", "r") as f:
    usuarios = json.load(f)

st.sidebar.header("🔐 Login")
usuario = st.sidebar.text_input("Usuário")
senha = st.sidebar.text_input("Senha", type="password")

if usuario not in usuarios:
    st.sidebar.warning("Usuário não encontrado.")
    st.stop()

senha_hash = usuarios[usuario]["senha"].encode()
if not bcrypt.checkpw(senha.encode(), senha_hash):
    st.sidebar.warning("Senha incorreta.")
    st.stop()

empresa_usuario = usuarios[usuario]["empresa"]
st.sidebar.success(f"Bem-vindo, {usuario}")

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

df = pd.read_csv(arquivo_csv)
if 'Data' in df.columns:
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df = df.dropna(subset=['Data'])

colunas_esperadas = {'Razao Social', 'Descricao', 'Data', 'vendas'}
if not colunas_esperadas.issubset(df.columns):
    st.error(f"Colunas ausentes: {colunas_esperadas - set(df.columns)}")
    st.stop()

# Navegação inicial de abas
aba = st.sidebar.radio("Escolha a visualização:", [
    "📊 Previsão por Produto", "🏆 Ranking de Vendas", "📌 Produtos Recomendados",
    "📉 Análise de Churn", "🔁 Previsão de Recompra", "📦 Pedido Sugerido"
])
st.subheader(f"Visualização selecionada: {aba}")
st.write("Aqui entrará o conteúdo dinâmico correspondente à aba.")
