import streamlit as st
import datetime
import json

st.set_page_config(page_title="EduAI Studio", layout="wide")

# =========================
# FUNÇÕES
# =========================

def formatar_data(data):
    return data.strftime("%d/%m/%Y")

def sugestoes_diagnostico(diag):
    base = {
        "TDAH": "atenção curta, precisa de estímulos visuais, dificuldade em manter foco contínuo",
        "TEA nível 1": "precisa de estrutura, clareza, pode ter dificuldade social leve",
        "TEA nível 2": "necessita apoio maior, precisa de previsibilidade e instruções claras",
        "TEA nível 3": "necessita alto suporte, linguagem simples e direta",
        "Dislexia": "dificuldade com leitura, melhor com visual e explicações orais curtas",
        "Discalculia": "dificuldade com números, precisa de exemplos concretos",
        "Processamento auditivo": "dificuldade em entender instruções longas, precisa de apoio visual",
        "Ansiedade": "pode travar sob pressão, precisa de segurança e progressão leve"
    }
    return base.get(diag, "")

# =========================
# TABS
# =========================

tabs = st.tabs([
    "1. Perfil da Criança",
    "2. Cronograma",
    "3. Configuração Didática",
    "4. Geração de Materiais"
])

# =========================
# ABA 1 — PERFIL
# =========================

with tabs[0]:
    st.header("Perfil da Criança")

    col1, col2 = st.columns(2)

    nome = col1.text_input("Nome")
    apelido = col2.text_input("Apelido")
    idade = col1.text_input("Idade")
    serie = col2.text_input("Série")

    escola = col1.text_input("Escola")
    turno = col2.text_input("Turno")

    interesses = st.text_area("Interesses")

    diagnostico = st.selectbox(
        "Diagnóstico",
        [
            "Nenhum",
            "TDAH",
            "TEA nível 1",
            "TEA nível 2",
            "TEA nível 3",
            "Dislexia",
            "Discalculia",
            "Processamento auditivo",
            "Ansiedade",
            "Outro"
        ]
    )

    outro_diag = ""
    if diagnostico == "Outro":
        outro_diag = st.text_input("Qual diagnóstico?")

    sugestao = sugestoes_diagnostico(diagnostico)

    outras = st.text_area(
        "Outras características (editável)",
        value=sugestao
    )

# =========================
# ABA 2 — CRONOGRAMA
# =========================

with tabs[1]:
    st.header("Plano de Estudo")

    materia = st.text_input("Matéria")
    conteudos = st.text_area("Conteúdos da prova")

    hoje = st.date_input("Data de hoje")
    prova = st.date_input("Data da prova")

    data_hoje = formatar_data(hoje)
    data_prova = formatar_data(prova)

    if st.button("Gerar Cronograma"):

        prompt = f"""
Criar cronograma de estudo até a prova

Aluno: {nome}
Série: {serie}

Matéria: {materia}
Conteúdos: {conteudos}

Data de hoje: {data_hoje}
Data da prova: {data_prova}

REGRAS:
- 1 conteúdo por dia
- sessões de 15 a 25 minutos
- incluir revisão no dia anterior
- não detalhar aula

FORMATO:
[DIA X]
Conteúdo:
Objetivo:
"""

        st.text_area("Cronograma", prompt, height=300)

# =========================
# ABA 3 — CONFIGURAÇÃO
# =========================

with tabs[2]:
    st.header("Configuração Didática")

    materia = st.text_input("Matéria", key="mat2")
    conteudo = st.text_input("Conteúdo do dia")

    hoje = st.date_input("Hoje", key="h2")
    prova = st.date_input("Prova", key="p2")

    estilo = st.text_area("Como a escola cobra")

    st.subheader("Tipos de material")

    gerar_video = st.checkbox("Vídeo")
    gerar_audio = st.checkbox("Áudio (responsável)")
    gerar_slide = st.checkbox("Slides")
    gerar_flash = st.checkbox("Flashcards (máx 10)")
    gerar_teste = st.checkbox("Teste")

# =========================
# ABA 4 — GERAÇÃO
# =========================

with tabs[3]:
    st.header("Gerar Materiais")

    if st.button("Gerar Prompt"):

        diag_final = outro_diag if diagnostico == "Outro" else diagnostico

        prompt = f"""
PROFESSOR PARTICULAR

Aluno: {nome} ({apelido})
Idade: {idade}
Série: {serie}
Escola: {escola}

Diagnóstico: {diag_final}
Características: {outras}

Interesses:
{interesses}

Matéria: {materia}
Conteúdo: {conteudo}

Forma de cobrança:
{estilo}

"""

        if gerar_video:
            prompt += "\nCriar vídeo explicativo\n"

        if gerar_audio:
            prompt += "\nCriar áudio para responsável (máx 5 min)\n"

        if gerar_slide:
            prompt += "\nCriar slides\n"

        if gerar_flash:
            prompt += "\nCriar até 10 flashcards\n"

        if gerar_teste:
            prompt += "\nCriar teste\n"

        prompt += """
REGRAS:
- adaptar ao perfil da criança
- não infantilizar
- usar exemplos claros
"""

        st.text_area("Prompt final", prompt, height=400)

        st.download_button("Baixar", prompt)
