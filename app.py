import datetime
import streamlit as st

from constants import (
    INTERESSES_OPTIONS,
    DIAG_OPTIONS,
    ATENCAO_OPTIONS,
    AUTONOMIA_OPTIONS,
    CANAL_OPTIONS,
    FRUSTRACAO_OPTIONS,
    NIVEL_OPTIONS,
    ERRO_OPTIONS,
    ENGAJAMENTO_OPTIONS,
    DIFICULDADE_OPTIONS,
    TRAVA_OPTIONS,
    RETOMADA_OPTIONS,
    ESCOLA_COBRANCA_OPTIONS,
    SITUACAO_OPTIONS,
    PRIORIDADE_OPTIONS,
    AREA_MATERIA_OPTIONS,
    STEPS,
)

from state import init_state, migrate_legacy_keys
from ui_components import inject_styles, checkbox_group, radio_group, slugify

from profile_logic import (
    formatar_data_br,
    atualizar_caracteristicas_sugeridas,
    get_perfil_data,
    obter_cobranca,
    extrair_campos_cronograma,
    save_named_profile,
    load_named_profile,
    resumo_aluno_compacto,
    modo_estudo,
)

from prompts import (
    contexto_studio_compacto,
    prompt_video,
    prompt_audio,
    prompt_slides,
    prompt_flash,
    prompt_teste,
    prompt_aula,
    prompt_cronograma,
)

st.set_page_config(page_title="🧠 EduAI Studio", layout="wide")
init_state()
migrate_legacy_keys()
inject_styles()

# =====================================================
# Helpers
# =====================================================

st.session_state.setdefault("saved_profiles", {})
st.session_state.setdefault("current_step", "Perfil")
st.session_state.setdefault("nav_message", "")
st.session_state.setdefault("nav_message_type", "info")


def set_msg(msg, kind="info"):
    st.session_state["nav_message"] = msg
    st.session_state["nav_message_type"] = kind


def clear_msg():
    st.session_state["nav_message"] = ""
    st.session_state["nav_message_type"] = "info"


def goto_step(step):
    st.session_state["current_step"] = step
    st.rerun()


def next_step():
    idx = STEPS.index(st.session_state["current_step"])
    if idx < len(STEPS) - 1:
        goto_step(STEPS[idx + 1])


def prev_step():
    idx = STEPS.index(st.session_state["current_step"])
    if idx > 0:
        goto_step(STEPS[idx - 1])


def footer_nav():
    c1, c2, c3 = st.columns([1, 1, 6])

    with c1:
        if st.button("⬅ Anterior", use_container_width=True):
            prev_step()

    with c2:
        if st.button("Próxima ➜", use_container_width=True):
            next_step()


def get_profile_base(date_obj=None):
    if date_obj is None:
        date_obj = datetime.date.today()

    atualizar_caracteristicas_sugeridas()

    return get_perfil_data(
        data_prova=formatar_data_br(date_obj)
    )


def copy_block(title, text, height=220):
    st.text_area(title, value=text, height=height, key=f"copy_{slugify(title)}")


# =====================================================
# Sidebar
# =====================================================

with st.sidebar:
    st.markdown("## Etapas")

    idx = STEPS.index(st.session_state["current_step"])
    st.progress((idx + 1) / len(STEPS))
    st.caption(f"Etapa {idx+1} de {len(STEPS)}")

    for step in STEPS:
        emoji = "👉 " if step == st.session_state["current_step"] else ""
        if st.button(f"{emoji}{step}", use_container_width=True, key=f"nav_{step}"):
            goto_step(step)

    st.markdown("---")
    st.markdown("## Perfis salvos")

    saved = list(st.session_state["saved_profiles"].keys())

    if not saved:
        st.caption("Nenhum perfil salvo.")
    else:
        for p in saved:
            if st.button(p, use_container_width=True, key=f"profile_{p}"):
                load_named_profile(p)
                atualizar_caracteristicas_sugeridas()
                set_msg(f"Perfil '{p}' carregado.", "success")
                st.rerun()

# =====================================================
# Header
# =====================================================

st.title("🧠 EduAI Studio")
st.caption("Materiais personalizados para estudo com prompts inteligentes.")

if st.session_state["nav_message"]:
    kind = st.session_state["nav_message_type"]
    if kind == "success":
        st.success(st.session_state["nav_message"])
    elif kind == "warning":
        st.warning(st.session_state["nav_message"])
    else:
        st.info(st.session_state["nav_message"])

# =====================================================
# Current Step
# =====================================================

step = st.session_state["current_step"]

# =====================================================
# PERFIL
# =====================================================

if step == "Perfil":
    st.subheader("Perfil do aluno")

    c1, c2 = st.columns(2)
    c1.text_input("Nome", key="nome")
    c2.text_input("Apelido", key="apelido")

    c1.text_input("Idade", key="idade")
    c2.text_input("Série / Ano", key="serie")

    c1.text_input("Escola", key="escola")
    c2.text_input("Turno", key="turno")

    st.text_input("Responsável", key="responsavel")

    st.markdown("### Interesses")
    checkbox_group(
        "Selecione os interesses",
        INTERESSES_OPTIONS,
        "interesses",
        columns=4
    )

    if "Outro" in st.session_state["interesses"]:
        st.text_input("Outro interesse", key="interesses_outro")

    st.markdown("### Diagnósticos")
    checkbox_group(
        "Selecione diagnósticos",
        DIAG_OPTIONS,
        "diagnosticos",
        columns=3
    )

    if "Outro" in st.session_state["diagnosticos"]:
        st.text_input("Outro diagnóstico", key="outro_diagnostico")

    atualizar_caracteristicas_sugeridas()

    st.text_area(
        "Características sugeridas automaticamente",
        value=st.session_state["caracteristicas_sugeridas"],
        height=140,
        disabled=True
    )

    st.text_area(
        "Outras características",
        key="outras_caracteristicas",
        height=120
    )

    st.markdown("### Salvar perfil")

    c1, c2 = st.columns([3, 1])
    c1.text_input("Nome para salvar", key="novo_nome_perfil")

    with c2:
        if st.button("Salvar"):
            nome = st.session_state["novo_nome_perfil"].strip()
            if nome:
                save_named_profile(nome)
                set_msg(f"Perfil '{nome}' salvo.", "success")
                st.rerun()

    footer_nav()

# =====================================================
# APRENDIZAGEM
# =====================================================

elif step == "Aprendizagem":
    st.subheader("Perfil de aprendizagem")

    radio_group("Atenção sustentada", ATENCAO_OPTIONS, "atencao_sustentada", True)
    radio_group("Autonomia", AUTONOMIA_OPTIONS, "autonomia", True)
    radio_group("Canal preferencial", CANAL_OPTIONS, "canal_preferencial", True)
    radio_group("Tolerância à frustração", FRUSTRACAO_OPTIONS, "tolerancia_frustracao", True)
    radio_group("Leitura", NIVEL_OPTIONS, "leitura_nivel", True)
    radio_group("Escrita", NIVEL_OPTIONS, "escrita_nivel", True)
    radio_group("Matemática", NIVEL_OPTIONS, "matematica_nivel", True)
    radio_group("Compreensão oral", ["Baixa", "Média", "Boa"], "compreensao_oral", True)

    st.markdown("### Erros e dificuldades")

    checkbox_group("Tipo de erro mais comum", ERRO_OPTIONS, "tipo_erro_mais_comum", 3)
    checkbox_group("O que mais engaja", ENGAJAMENTO_OPTIONS, "engajamento", 3)
    checkbox_group("Principal dificuldade", DIFICULDADE_OPTIONS, "principal_dificuldade", 3)
    checkbox_group("Sinais quando trava", TRAVA_OPTIONS, "sinais_quando_trava", 3)
    checkbox_group("Melhor forma de retomar", RETOMADA_OPTIONS, "melhor_forma_retomar", 3)

    footer_nav()

# =====================================================
# CRONOGRAMA
# =====================================================

elif step == "Cronograma":
    st.subheader("Cronograma até a prova")

    st.text_input("Matéria", key="cron_materia")
    st.selectbox("Área da matéria", AREA_MATERIA_OPTIONS, key="cron_area_materia")

    hoje = st.date_input("Hoje", datetime.date.today(), key="cron_hoje")
    prova = st.date_input("Prova", datetime.date.today(), key="cron_prova")

    st.text_area("Conteúdos da prova", key="cron_conteudos", height=120)

    c1, c2, c3 = st.columns(3)
    c1.text_area("Alta prioridade", key="cron_alta")
    c2.text_area("Média prioridade", key="cron_media")
    c3.text_area("Baixa prioridade", key="cron_baixa")

    perfil = get_profile_base(prova)

    txt = prompt_cronograma(
        perfil,
        st.session_state["cron_materia"],
        st.session_state["cron_area_materia"],
        st.session_state["cron_conteudos"],
        formatar_data_br(hoje),
        formatar_data_br(prova),
        st.session_state["cron_alta"],
        st.session_state["cron_media"],
        st.session_state["cron_baixa"],
    )

    with st.expander("Prompt de cronograma"):
        copy_block("Prompt Cronograma", txt, 380)

    st.markdown("### Usar linha do cronograma")

    st.text_area("Cole aqui a linha do dia", key="cronograma_linha_do_dia", height=90)

    if st.button("Usar esta linha na Configuração"):
        campos = extrair_campos_cronograma(st.session_state["cronograma_linha_do_dia"])

        st.session_state["mat_did"] = st.session_state["cron_materia"]
        st.session_state["config_area_materia"] = st.session_state["cron_area_materia"]
        st.session_state["conteudo_dia"] = campos["texto_colar"] or campos["conteudo"]
        st.session_state["objetivo_dia"] = campos["objetivo"]

        goto_step("Configuração")

    footer_nav()

# =====================================================
# CONFIGURAÇÃO
# =====================================================

elif step == "Configuração":
    st.subheader("Configuração do estudo")

    st.text_input("Matéria", key="mat_did")
    st.selectbox("Área da matéria", AREA_MATERIA_OPTIONS, key="config_area_materia")

    st.text_area("Conteúdo do dia", key="conteudo_dia", height=140)
    st.text_input("Objetivo do dia", key="objetivo_dia")

    hoje = st.date_input("Hoje", datetime.date.today(), key="config_hoje")
    prova = st.date_input("Prova", datetime.date.today(), key="config_prova")

    radio_group("Situação", SITUACAO_OPTIONS, "situacao_conteudo", True)
    radio_group("Prioridade", PRIORIDADE_OPTIONS, "prioridade_conteudo", True)

    st.toggle("Usar anexos apenas como embasamento", key="usa_fontes")

    checkbox_group(
        "Materiais",
        ["Vídeo", "Áudio (responsável)", "Slides", "Flashcards (máx 10)", "Teste"],
        "selected_materials",
        3
    )

    footer_nav()

# =====================================================
# STUDIO
# =====================================================

elif step == "Studio":
    hoje = st.session_state.get("config_hoje", datetime.date.today())
    prova = st.session_state.get("config_prova", datetime.date.today())

    days = (prova - hoje).days

    perfil = get_profile_base(prova)

    materia = st.session_state["mat_did"]
    area = st.session_state["config_area_materia"]
    conteudo = st.session_state["conteudo_dia"]
    objetivo = st.session_state["objetivo_dia"]
    estilo = obter_cobranca()
    situacao = st.session_state["situacao_conteudo"]
    prioridade = st.session_state["prioridade_conteudo"]
    usa = st.session_state["usa_fontes"]

    st.subheader("Studio")

    tabs = st.tabs(["Vídeo", "Áudio", "Slides", "Flashcards", "Teste"])

    with tabs[0]:
        copy_block(
            "Prompt Vídeo",
            prompt_video(
                perfil, materia, area, conteudo, objetivo,
                estilo, situacao, prioridade, days,
                usa, resumo_aluno_compacto
            ),
            300
        )

    with tabs[1]:
        copy_block(
            "Prompt Áudio",
            prompt_audio(
                perfil, materia, area, conteudo, objetivo,
                estilo, situacao, prioridade, days,
                usa, resumo_aluno_compacto
            ),
            300
        )

    with tabs[2]:
        copy_block(
            "Prompt Slides",
            prompt_slides(
                perfil, materia, area, conteudo, objetivo,
                estilo, situacao, prioridade, days,
                usa, resumo_aluno_compacto
            ),
            300
        )

    with tabs[3]:
        copy_block(
            "Prompt Flashcards",
            prompt_flash(
                perfil, materia, area, conteudo, objetivo,
                estilo, situacao, prioridade, days,
                usa, resumo_aluno_compacto
            ),
            300
        )

    with tabs[4]:
        copy_block(
            "Prompt Teste",
            prompt_teste(
                perfil, materia, area, conteudo, objetivo,
                estilo, situacao, prioridade, days,
                usa, resumo_aluno_compacto
            ),
            300
        )

    footer_nav()

# =====================================================
# AULA COMPLETA
# =====================================================

elif step == "Aula Completa":
    hoje = st.session_state.get("config_hoje", datetime.date.today())
    prova = st.session_state.get("config_prova", datetime.date.today())

    days = (prova - hoje).days
    perfil = get_profile_base(prova)

    aula = prompt_aula(
        perfil,
        st.session_state["mat_did"],
        st.session_state["config_area_materia"],
        st.session_state["conteudo_dia"],
        st.session_state["objetivo_dia"],
        obter_cobranca(),
        st.session_state["situacao_conteudo"],
        st.session_state["prioridade_conteudo"],
        days,
        st.session_state["selected_materials"],
        st.session_state["usa_fontes"],
        modo_estudo,
    )

    st.subheader("Aula completa")
    copy_block("Pacote completo", aula, 520)

    footer_nav()
