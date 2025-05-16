
import streamlit as st
import bcrypt
import json
import os

st.set_page_config(page_title="Cadastro de Usuário", layout="centered")
st.title("🧾 Cadastro de Novo Usuário")

arquivo = "usuarios.json"

# Carregar usuários existentes
if os.path.exists(arquivo):
    with open(arquivo, "r") as f:
        usuarios = json.load(f)
else:
    usuarios = {}

# Formulário
novo_usuario = st.text_input("Novo usuário:")
nova_senha = st.text_input("Senha:", type="password")
empresa = st.selectbox("Empresa:", ["Brasforma", "Fort Solutions", "Padaria Cepam", "ALL (Admin)"])

if st.button("Cadastrar"):
    if novo_usuario in usuarios:
        st.error("Usuário já existe.")
    elif not novo_usuario or not nova_senha:
        st.warning("Usuário e senha são obrigatórios.")
    else:
        hash_senha = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
        usuarios[novo_usuario] = {"senha": hash_senha, "empresa": "ALL" if empresa.startswith("ALL") else empresa}
        with open(arquivo, "w") as f:
            json.dump(usuarios, f, indent=2)
        st.success(f"Usuário '{novo_usuario}' cadastrado com sucesso!")
        st.balloons()
