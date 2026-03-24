# Versão simplificada com novos campos estratégicos
import streamlit as st
import datetime
import json

st.set_page_config(page_title="EduAI Studio", layout="wide")

def date_br(d):
    return d.strftime("%d/%m/%Y")

st.title("🧠 EduAI Studio — Ensino Personalizado")

tabs = st.tabs([
    "1. Perfil da Criança",
    "2. Configuração Didática",
    "3. Geração de Materiais"
])

# =========================
# ABA 1
# =========================
with tabs[0]:
    st.header("Perfil da Criança")

    nome = st.text_input("Nome")
    apelido = st.text_input("Apelido")
    idade = st.text_input("Idade")
    serie = st.text_input("Série")
    escola = st.text_input("Escola")
    interesses = st.text_area("Interesses")

    diagnostico = st.selectbox(
        "Diagnóstico",
        ["Nenhum", "TDAH", "TEA", "Dislexia", "Discalculia", "Outro"]
    )

    outras = st.text_area("Outras características")

# =========================
# ABA 2
# =========================
with tabs[1]:
    st.header("Configuração Didática")

    materia = st.text_input("Matéria")
    conteudo = st.text_input("Conteúdo do dia")

    hoje = st.date_input("Data de hoje", datetime.date.today())
    prova = st.date_input("Data da prova", datetime.date.today())

    livro = st.text_input("Livro (opcional)")
    editora = st.text_input("Editora (opcional)")
    edicao = st.text_input("Edição (opcional)")

    estilo = st.text_area("Como a escola cobra")

# =========================
# ABA 3
# =========================
with tabs[2]:
    st.header("Geração de Materiais")

    if st.button("Gerar Prompt Completo"):

        prompt = f"""PROFESSOR PARTICULAR

Aluno: {nome} ({apelido})
Idade: {idade}
Série: {serie}
Escola: {escola}

Perfil:
Diagnóstico: {diagnostico}
Características: {outras}

Interesses:
{interesses}

Matéria: {materia}
Conteúdo: {conteudo}

Referência didática:
Livro: {livro}
Editora: {editora}
Edição: {edicao}

Forma de cobrança:
{estilo}

INSTRUÇÕES:
- Criar vídeo
- Criar áudio para responsável (máx 5 min)
- Criar slides
- Criar até 10 flashcards
- Criar resumo

- Não usar fontes externas
- Adaptar ao perfil da criança
"""

        st.text_area("Prompt gerado", prompt, height=400)

        st.download_button(
            "Baixar Prompt",
            prompt,
            file_name="prompt_eduai.txt"
        )

