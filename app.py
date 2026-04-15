# app.py
# V8 CLEAN - versão completa com correção de checkbox persistente integrada

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

# ======================================================
# CONFIG
# ======================================================

st.set_page_config(
    page_title="EduAI Studio",
    page_icon="🧠",
    layout="wide"
)

init_state()
migrate_legacy_keys()
inject_styles()

# ======================================================
# DEFAULTS EXTRA
# ======================================================

st.session_state.setdefault("current_step", "Perfil")
st.session_state.setdefault("saved_profiles", {})
st.session_state.setdefault("novo_nome_perfil", "")
st.session_state.setdefault("nav_message", "")
st.session_state.setdefault("nav_message_type", "info")

# ======================================================
# HELPERS
# ======================================================

def set_nav_message(msg, tp="info"):
    st.session_state["nav_message"] = msg
    st.session_state["nav_message_type"] = tp


def clear_nav_message():
    st.session_state["nav_message"] = ""
    st.session_state["nav_message_type"] = "info"


def sync_checkbox_group_keys(state_key, options):
    selected = set(st.session_state.get(state_key, []))
    for option in options:
        widget_key = f"{state_key}_{slugify(option)}"
        st.session_state[widget_key] = option in selected


def sync_all_checkbox_groups():
    sync_checkbox_group_keys("interesses", INTERESSES_OPTIONS)
    sync_checkbox_group_keys("diagnosticos", DIAG_OPTIONS)
    sync_checkbox_group_keys("tipo_erro_mais_comum", ERRO_OPTIONS)
    sync_checkbox_group_keys("engajamento", ENGAJAMENTO_OPTIONS)
    sync_checkbox_group_keys("principal_dificuldade", DIFICULDADE_OPTIONS)
    sync_checkbox_group_keys("sinais_quando_trava", TRAVA_OPTIONS)
    sync_checkbox_group_keys("melhor_forma_retomar", RETOMADA_OPTIONS)
    sync_checkbox_group_keys("cobranca_escola", ESCOLA_COBRANCA_OPTIONS)
    sync_checkbox_group_keys(
        "selected_materials",
        ["Vídeo", "Áudio (responsável)", "Slides", "Flashcards (máx 10)", "Teste"]
    )


def get_profile():
    atualizar_caracteristicas_sugeridas()
    return get_perfil_data()


def goto_step(step_name):
    st.session_state["current_step"] = step_name
    st.rerun()


def next_step():
    idx = STEPS.index(st.session_state["current_step"])
    if idx < len(STEPS) - 1:
        goto_step(STEPS[idx + 1])


def prev_step():
    idx = STEPS.index(st.session_state["current_step"])
    if idx > 0:
        goto_step(STEPS[idx - 1])


def copy_box(label, text, key):
    st.text_area(label, value=text, height=220, key=f"txt_{key}")
    st.code(text)
    st.caption("Selecione acima e copie")


# ======================================================
# SIDEBAR
# ======================================================

with st.sidebar:
    st.markdown("## Etapas")

    current_idx = STEPS.index(st.session_state["current_step"])
    st.progress((current_idx + 1) / len(STEPS))
    st.caption(f"Etapa {current_idx + 1} de {len(STEPS)}")

    for step in STEPS:
        emoji = "👉 " if step == st.session_state["current_step"] else ""
        if st.button(f"{emoji}{step}", use_container_width=True):
            goto_step(step)

    st.markdown("---")
    st.markdown("## Perfis salvos")

    perfis = list(st.session_state["saved_profiles"].keys())

    if perfis:
        perfil_sel = st.selectbox("Escolha", perfis, key="perfil_sidebar")

        c1, c2 = st.columns(2)

        with c1:
            if st.button("Carregar", use_container_width=True):
                load_named_profile(perfil_sel)
                sync_all_checkbox_groups()
                atualizar_caracteristicas_sugeridas()
                set_nav_message(f"Perfil '{perfil_sel}' carregado.", "success")
                st.rerun()

        with c2:
            if st.button("Excluir", use_container_width=True):
                del st.session_state["saved_profiles"][perfil_sel]
                set_nav_message("Perfil excluído.", "success")
                st.rerun()
    else:
        st.caption("Nenhum perfil salvo.")


# ======================================================
# HEADER
# ======================================================

st.title("🧠 EduAI Studio - V8 Clean")
st.caption("Fluxo simplificado e prompts otimizados para NotebookLM")

if st.session_state["nav_message"]:
    tp = st.session_state["nav_message_type"]

    if tp == "success":
        st.success(st.session_state["nav_message"])
    elif tp == "warning":
        st.warning(st.session_state["nav_message"])
    else:
        st.info(st.session_state["nav_message"])

# ======================================================
# FOOTER NAV
# ======================================================

def footer_nav():
    c1, c2, c3 = st.columns([1, 1, 4])

    with c1:
        if st.button("⬅ Anterior"):
            prev_step()

    with c2:
        if st.button("Próximo ➜"):
            next_step()


# ======================================================
# SCREEN ROUTER
# ======================================================

step = st.session_state["current_step"]

# ======================================================
# PERFIL
# ======================================================

if step == "Perfil":

    st.subheader("Dados básicos")

    c1, c2 = st.columns(2)
    c1.text_input("Nome", key="nome")
    c2.text_input("Apelido", key="apelido")

    c1.text_input("Idade", key="idade")
    c2.text_input("Série / Ano", key="serie")

    c1.text_input("Escola", key="escola")
    c2.text_input("Turno", key="turno")

    st.text_input("Responsável", key="responsavel")

    st.markdown("---")

    checkbox_group(
        "Interesses",
        INTERESSES_OPTIONS,
        "interesses",
        columns=4
    )

    if "Outro" in st.session_state["interesses"]:
        st.text_input("Outro interesse", key="interesses_outro")

    st.markdown("---")

    checkbox_group(
        "Diagnósticos",
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
        height=160,
        disabled=True
    )

    st.text_area(
        "Outras características",
        key="outras_caracteristicas",
        height=120
    )

    st.markdown("---")
    st.subheader("Salvar perfil")

    c1, c2 = st.columns([3, 1])

    c1.text_input(
        "Nome para salvar",
        key="novo_nome_perfil"
    )

    with c2:
        if st.button("Salvar"):
            nome = st.session_state["novo_nome_perfil"].strip()
            if nome:
                save_named_profile(nome)
                set_nav_message("Perfil salvo.", "success")
                st.rerun()

    footer_nav()

# ======================================================
# APRENDIZAGEM
# ======================================================

elif step == "Aprendizagem":

    radio_group("Atenção sustentada", ATENCAO_OPTIONS, "atencao_sustentada")
    radio_group("Autonomia", AUTONOMIA_OPTIONS, "autonomia")
    radio_group("Canal preferencial", CANAL_OPTIONS, "canal_preferencial")
    radio_group("Tolerância à frustração", FRUSTRACAO_OPTIONS, "tolerancia_frustracao")

    radio_group("Leitura", NIVEL_OPTIONS, "leitura_nivel")
    radio_group("Escrita", NIVEL_OPTIONS, "escrita_nivel")
    radio_group("Matemática", NIVEL_OPTIONS, "matematica_nivel")

    st.markdown("---")

    checkbox_group(
        "Tipo de erro mais comum",
        ERRO_OPTIONS,
        "tipo_erro_mais_comum",
        columns=3
    )

    checkbox_group(
        "O que mais engaja",
        ENGAJAMENTO_OPTIONS,
        "engajamento",
        columns=3
    )

    checkbox_group(
        "Principal dificuldade",
        DIFICULDADE_OPTIONS,
        "principal_dificuldade",
        columns=3
    )

    checkbox_group(
        "Sinais quando trava",
        TRAVA_OPTIONS,
        "sinais_quando_trava",
        columns=3
    )

    checkbox_group(
        "Melhor forma de retomar",
        RETOMADA_OPTIONS,
        "melhor_forma_retomar",
        columns=3
    )

    footer_nav()

# ======================================================
# CRONOGRAMA
# ======================================================

elif step == "Cronograma":

    st.text_input("Matéria", key="cron_materia")

    st.selectbox(
        "Área",
        AREA_MATERIA_OPTIONS,
        key="cron_area_materia"
    )

    hoje = st.date_input("Hoje", key="cron_hoje_input")
    prova = st.date_input("Data da prova", key="cron_prova_input")

    st.caption(f"Hoje: {formatar_data_br(hoje)}")
    st.caption(f"Prova: {formatar_data_br(prova)}")

    st.text_area("Conteúdos", key="cron_conteudos", height=120)

    txt = prompt_cronograma(
        get_profile(),
        st.session_state["cron_materia"],
        st.session_state["cron_area_materia"],
        st.session_state["cron_conteudos"],
        formatar_data_br(hoje),
        formatar_data_br(prova),
        "",
        "",
        ""
    )

    copy_box("Prompt do cronograma", txt, "cron")

    st.text_area(
        "Linha do dia",
        key="cronograma_linha_do_dia",
        height=90
    )

    if st.button("Usar esta linha na Configuração"):
        campos = extrair_campos_cronograma(
            st.session_state["cronograma_linha_do_dia"]
        )

        st.session_state["mat_did"] = st.session_state["cron_materia"]
        st.session_state["config_area_materia"] = st.session_state["cron_area_materia"]
        st.session_state["conteudo_dia"] = campos["texto_colar"]
        st.session_state["objetivo_dia"] = campos["objetivo"]
        st.session_state["config_did_prova"] = prova

        set_nav_message("Linha enviada para Configuração.", "success")

    footer_nav()

# ======================================================
# CONFIGURAÇÃO
# ======================================================

elif step == "Configuração":

    st.text_input("Matéria", key="mat_did")

    st.selectbox(
        "Área",
        AREA_MATERIA_OPTIONS,
        key="config_area_materia"
    )

    st.text_area(
        "Conteúdo do dia",
        key="conteudo_dia",
        height=120
    )

    st.text_input(
        "Objetivo",
        key="objetivo_dia"
    )

    hoje2 = st.date_input("Hoje", key="config_did_hoje")
    prova2 = st.date_input("Data da prova", key="config_did_prova")

    radio_group(
        "Situação do conteúdo",
        SITUACAO_OPTIONS,
        "situacao_conteudo"
    )

    radio_group(
        "Prioridade",
        PRIORIDADE_OPTIONS,
        "prioridade_conteudo"
    )

    checkbox_group(
        "Como a escola cobra",
        ESCOLA_COBRANCA_OPTIONS,
        "cobranca_escola",
        columns=3
    )

    checkbox_group(
        "Materiais",
        ["Vídeo", "Áudio (responsável)", "Slides", "Flashcards (máx 10)", "Teste"],
        "selected_materials",
        columns=3
    )

    footer_nav()

# ======================================================
# STUDIO
# ======================================================

elif step == "Studio":

    prova = st.session_state.get("config_did_prova", datetime.date.today())
    hoje = st.session_state.get("config_did_hoje", datetime.date.today())
    dias = (prova - hoje).days

    perfil = get_profile()
    estilo = obter_cobranca()

    materia = st.session_state["mat_did"]
    area = st.session_state["config_area_materia"]
    conteudo = st.session_state["conteudo_dia"]
    situacao = st.session_state["situacao_conteudo"]
    prioridade = st.session_state["prioridade_conteudo"]

    materiais = st.session_state["selected_materials"]

    if "Vídeo" in materiais:
        copy_box(
            "Prompt Vídeo",
            prompt_video(
                perfil, materia, area, conteudo,
                estilo, situacao, prioridade,
                dias, False
            ),
            "video"
        )

    if "Áudio (responsável)" in materiais:
        copy_box(
            "Prompt Áudio",
            prompt_audio(
                perfil, materia, area, conteudo,
                estilo, situacao, prioridade,
                dias, False
            ),
            "audio"
        )

    if "Slides" in materiais:
        copy_box(
            "Prompt Slides",
            prompt_slides(
                perfil, materia, area, conteudo,
                estilo, situacao, prioridade,
                dias, False
            ),
            "slides"
        )

    if "Flashcards (máx 10)" in materiais:
        copy_box(
            "Prompt Flashcards",
            prompt_flash(
                perfil, materia, area, conteudo,
                estilo, situacao, prioridade,
                dias, False
            ),
            "flash"
        )

    if "Teste" in materiais:
        copy_box(
            "Prompt Teste",
            prompt_teste(
                perfil, materia, area, conteudo,
                estilo, situacao, prioridade,
                dias, False
            ),
            "teste"
        )

    footer_nav()

# ======================================================
# AULA COMPLETA
# ======================================================

elif step == "Aula Completa":

    prova = st.session_state.get("config_did_prova", datetime.date.today())
    hoje = st.session_state.get("config_did_hoje", datetime.date.today())
    dias = (prova - hoje).days

    txt = prompt_aula(
        get_profile(),
        st.session_state["mat_did"],
        st.session_state["config_area_materia"],
        st.session_state["conteudo_dia"],
        obter_cobranca(),
        st.session_state["situacao_conteudo"],
        st.session_state["prioridade_conteudo"],
        dias,
        st.session_state["selected_materials"],
        False
    )

    copy_box("Pacote completo", txt, "aula")

    footer_nav()
