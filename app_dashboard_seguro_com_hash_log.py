
import streamlit as st
st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

import pandas as pd
import os
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import matplotlib.pyplot as plt
import bcrypt
import json

# === Login com JSON externo ===
with open("usuarios.json", "r") as f:
    usuarios = json.load(f)

st.sidebar.title("🔐 Login")
usuario = st.sidebar.text_input("Usuário")
senha = st.sidebar.text_input("Senha", type="password")

if usuario not in usuarios:
    st.sidebar.warning("Usuário não encontrado.")
    st.stop()

senha_hash = usuarios[usuario]["senha"].encode()
if not bcrypt.checkpw(senha.encode(), senha_hash):
    st.sidebar.warning("Senha incorreta.")
    st.stop()

# Registrar log
from datetime import datetime
import socket
log = {
    "usuario": usuario,
    "empresa": usuarios[usuario]["empresa"],
    "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "ip": socket.gethostbyname(socket.gethostname())
}
import csv
with open("log_acessos.csv", "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=log.keys())
    if f.tell() == 0:
        writer.writeheader()
    writer.writerow(log)


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

