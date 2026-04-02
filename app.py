import streamlit as st
import datetime
import json

st.set_page_config(page_title="EduAI Studio", page_icon="🧠", layout="wide")

# ======================
# CONSTANTES
# ======================

PT_MONTHS = {
    1:"janeiro",2:"fevereiro",3:"março",4:"abril",5:"maio",6:"junho",
    7:"julho",8:"agosto",9:"setembro",10:"outubro",11:"novembro",12:"dezembro"
}

DIAG_OPTIONS = ["TDAH","TEA nível 1","TEA nível 2","TEA nível 3","Dislexia","Discalculia","Processamento auditivo","Ansiedade","TOD","Outro"]

ESCOLA_COBRANCA_OPTIONS = [
    "questões objetivas","questões dissertativas","interpretação de texto",
    "interpretação com imagens","situações do cotidiano","passo a passo",
    "comparação","verdadeiro ou falso","completar lacunas","gráficos/tabelas"
]

INTENSIDADE_OPTIONS = ["Essencial","Forte","Profundo","Prova difícil"]

ENGAJAMENTO_OPTIONS = ["desafios","competição leve","visual","histórias","jogos","curiosidades","prático","Outro"]
DIFICULDADE_OPTIONS = ["atenção","interpretação","organização","memória","resolver sozinho","Outro"]
TRAVA_OPTIONS = ["dispersa","trava","chuta","ansioso","quer parar","Outro"]
RETOMADA_OPTIONS = ["dividir","visual","exemplo","pergunta simples","pausa","reforço","Outro"]

# ======================
# DEFAULTS
# ======================

DEFAULTS = {
    "nome":"","apelido":"","idade":"","serie":"","escola":"","turno":"",
    "interesses":"","responsavel":"",
    "diagnosticos":[],"outro_diagnostico":"",
    "engajamento":[],"engajamento_outro":"",
    "principal_dificuldade":[],"dificuldade_outro":"",
    "sinais_trava":[],"trava_outro":"",
    "retomada":[],"retomada_outro":"",
    "intensidade":"Forte",
    "cobranca_escola":[],"cobranca_extra":"",
    "selected_materials":["Vídeo","Slides"]
}

for k,v in DEFAULTS.items():
    st.session_state.setdefault(k,v)

# ======================
# FUNÇÕES AUXILIARES
# ======================

def juntar(lista, outro):
    itens=[x for x in lista if x!="Outro"]
    if outro.strip():
        itens.append(outro.strip())
    return ", ".join(itens) if itens else "não informado"

def resumo_aluno():
    return f"""
Aluno {st.session_state['nome']} ({st.session_state['serie']})
Diagnóstico: {", ".join(st.session_state['diagnosticos']) or "nenhum"}
Engaja com: {juntar(st.session_state["engajamento"], st.session_state["engajamento_outro"])}
Dificuldade: {juntar(st.session_state["principal_dificuldade"], st.session_state["dificuldade_outro"])}
Trava: {juntar(st.session_state["sinais_trava"], st.session_state["trava_outro"])}
Retomar: {juntar(st.session_state["retomada"], st.session_state["retomada_outro"])}
""".strip()

def contexto_compacto(materia,conteudo,dias,estilo):
    return f"""Crie material de estudo.
Matéria: {materia}
Conteúdo: {conteudo}
Dias prova: {dias}
Cobrança: {estilo or 'não informado'}

Perfil:
{resumo_aluno()}

Regras:
- direto e claro
- adaptado ao aluno
- sem enrolação
- útil para estudo real
"""

# ======================
# PROMPTS ENXUTOS (STUDIO)
# ======================

def prompt_video(materia,conteudo,dias,estilo):
    return contexto_compacto(materia,conteudo,dias,estilo)+"""
Crie roteiro de vídeo:
- objetivo
- explicação simples
- 2 exemplos
- 1 erro comum
- mini revisão
"""

def prompt_audio(materia,conteudo,dias,estilo):
    return contexto_compacto(materia,conteudo,dias,estilo)+"""
Crie áudio para responsável:
- objetivo
- como explicar
- onde trava
- como ajudar
- como revisar
"""

def prompt_slides(materia,conteudo,dias,estilo):
    return contexto_compacto(materia,conteudo,dias,estilo)+"""
Crie slides:
- conceito
- exemplo
- erro comum
- prática
- revisão
"""

def prompt_flash(materia,conteudo,dias,estilo):
    return contexto_compacto(materia,conteudo,dias,estilo)+"""
Crie 6 flashcards:
- pergunta
- resposta
- foco em fixação
"""

def prompt_teste(materia,conteudo,dias,estilo):
    return contexto_compacto(materia,conteudo,dias,estilo)+"""
Crie teste:
- 5 questões
- gabarito comentado
"""

# ======================
# UI
# ======================

st.title("🧠 EduAI Studio v6.1")

tabs = st.tabs(["Perfil","Aprendizagem","Configuração","Studio"])

# ======================
# PERFIL
# ======================

with tabs[0]:
    st.session_state["nome"]=st.text_input("Nome",value=st.session_state["nome"])
    st.session_state["serie"]=st.text_input("Série",value=st.session_state["serie"])
    st.session_state["diagnosticos"]=st.multiselect("Diagnóstico",DIAG_OPTIONS)

# ======================
# APRENDIZAGEM
# ======================

with tabs[1]:
    st.subheader("Engajamento")
    st.session_state["engajamento"]=st.multiselect("",ENGAJAMENTO_OPTIONS)
    if "Outro" in st.session_state["engajamento"]:
        st.session_state["engajamento_outro"]=st.text_input("Outro")

    st.subheader("Dificuldade")
    st.session_state["principal_dificuldade"]=st.multiselect("",DIFICULDADE_OPTIONS)
    if "Outro" in st.session_state["principal_dificuldade"]:
        st.session_state["dificuldade_outro"]=st.text_input("Outro")

    st.subheader("Trava")
    st.session_state["sinais_trava"]=st.multiselect("",TRAVA_OPTIONS)
    if "Outro" in st.session_state["sinais_trava"]:
        st.session_state["trava_outro"]=st.text_input("Outro")

    st.subheader("Retomada")
    st.session_state["retomada"]=st.multiselect("",RETOMADA_OPTIONS)
    if "Outro" in st.session_state["retomada"]:
        st.session_state["retomada_outro"]=st.text_input("Outro")

# ======================
# CONFIG
# ======================

with tabs[2]:
    materia=st.text_input("Matéria")
    conteudo=st.text_input("Conteúdo")
    prova=st.date_input("Data prova")
    dias=(prova-datetime.date.today()).days

    st.session_state["cobranca_escola"]=st.multiselect("Cobrança",ESCOLA_COBRANCA_OPTIONS)
    estilo=", ".join(st.session_state["cobranca_escola"])

# ======================
# STUDIO
# ======================

with tabs[3]:
    st.subheader("Prompts otimizados")

    st.text_area("Vídeo",value=prompt_video(materia,conteudo,dias,estilo),height=180)
    st.text_area("Áudio",value=prompt_audio(materia,conteudo,dias,estilo),height=180)
    st.text_area("Slides",value=prompt_slides(materia,conteudo,dias,estilo),height=180)
    st.text_area("Flashcards",value=prompt_flash(materia,conteudo,dias,estilo),height=180)
    st.text_area("Teste",value=prompt_teste(materia,conteudo,dias,estilo),height=180)
