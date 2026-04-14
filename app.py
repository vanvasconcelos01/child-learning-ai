import datetime
import json
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
from ui_components import inject_styles, checkbox_group
from profile_logic import (
    formatar_data_br,
    atualizar_caracteristicas_sugeridas,
    get_perfil_data,
    obter_cobranca,
    extrair_campos_cronograma,
    resumo_aluno_compacto,
    modo_estudo,
)
from prompts import (
    prompt_video,
    prompt_audio,
    prompt_slides,
    prompt_flash,
    prompt_teste,
    prompt_aula,
    prompt_cronograma,
)
from storage import load_saved_profiles, save_saved_profiles

st.set_page_config(page_title="EduAI Studio", page_icon="🧠", layout="wide")
init_state()
migrate_legacy_keys()
inject_styles()

st.session_state.setdefault("saved_profiles", {})
st.session_state.setdefault("current_step", "Perfil")
st.session_state.setdefault("nav_message", "")
st.session_state.setdefault("nav_message_type", "info")
st.session_state.setdefault("mostrar_debug", False)
st.session_state.setdefault("perfil_sidebar_select", "")

if not st.session_state["saved_profiles"]:
    st.session_state["saved_profiles"] = load_saved_profiles()


# =====================================================
# Helpers
# =====================================================

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
    c1, c2, _ = st.columns([1, 1, 6])

    with c1:
        if STEPS.index(st.session_state["current_step"]) > 0:
            if st.button("⬅ Anterior", use_container_width=True, key=f"prev_{st.session_state['current_step']}"):
                prev_step()

    with c2:
        if STEPS.index(st.session_state["current_step"]) < len(STEPS) - 1:
            if st.button("Próxima ➜", use_container_width=True, key=f"next_{st.session_state['current_step']}"):
                next_step()


def get_profile_base(date_obj=None):
    if date_obj is None:
        date_obj = datetime.date.today()
    atualizar_caracteristicas_sugeridas()
    return get_perfil_data(formatar_data_br(date_obj))


def show_prompt_block(title: str, text: str, key_suffix: str):
    st.markdown(f"#### {title}")
    st.code(text, language="text")
    with st.expander("Visualizar em caixa de texto"):
        st.text_area(
            f"{title} (visualização)",
            value=text,
            height=220,
            key=f"view_{key_suffix}",
        )


def collect_profile_payload():
    atualizar_caracteristicas_sugeridas()
    return {
        "nome": st.session_state["nome"],
        "apelido": st.session_state["apelido"],
        "idade": st.session_state["idade"],
        "serie": st.session_state["serie"],
        "escola": st.session_state["escola"],
        "turno": st.session_state["turno"],
        "responsavel": st.session_state["responsavel"],
        "interesses": st.session_state["interesses"],
        "interesses_outro": st.session_state["interesses_outro"],
        "diagnosticos": st.session_state["diagnosticos"],
        "outro_diagnostico": st.session_state["outro_diagnostico"],
        "outras_caracteristicas": st.session_state["outras_caracteristicas"],
        "caracteristicas_sugeridas": st.session_state["caracteristicas_sugeridas"],
        "atencao_sustentada": st.session_state["atencao_sustentada"],
        "autonomia": st.session_state["autonomia"],
        "canal_preferencial": st.session_state["canal_preferencial"],
        "tolerancia_frustracao": st.session_state["tolerancia_frustracao"],
        "leitura_nivel": st.session_state["leitura_nivel"],
        "escrita_nivel": st.session_state["escrita_nivel"],
        "matematica_nivel": st.session_state["matematica_nivel"],
        "compreensao_oral": st.session_state["compreensao_oral"],
        "tipo_erro_mais_comum": st.session_state["tipo_erro_mais_comum"],
        "tipo_erro_outro": st.session_state["tipo_erro_outro"],
        "engajamento": st.session_state["engajamento"],
        "engajamento_outro": st.session_state["engajamento_outro"],
        "principal_dificuldade": st.session_state["principal_dificuldade"],
        "dificuldade_outro": st.session_state["dificuldade_outro"],
        "sinais_quando_trava": st.session_state["sinais_quando_trava"],
        "trava_outro": st.session_state["trava_outro"],
        "melhor_forma_retomar": st.session_state["melhor_forma_retomar"],
        "retomada_outro": st.session_state["retomada_outro"],
    }


def apply_profile_payload(payload: dict):
    for k, v in payload.items():
        st.session_state[k] = v
    atualizar_caracteristicas_sugeridas()


def save_profile_to_disk(profile_name: str):
    profiles = load_saved_profiles()
    profiles[profile_name] = collect_profile_payload()
    save_saved_profiles(profiles)
    st.session_state["saved_profiles"] = profiles


def load_profile_from_disk(profile_name: str):
    profiles = load_saved_profiles()
    payload = profiles.get(profile_name)
    if payload:
        apply_profile_payload(payload)
        st.session_state["saved_profiles"] = profiles


def delete_profile_from_disk(profile_name: str):
    profiles = load_saved_profiles()
    if profile_name in profiles:
        del profiles[profile_name]
        save_saved_profiles(profiles)
    st.session_state["saved_profiles"] = profiles


def apply_cronograma_to_config():
    campos = extrair_campos_cronograma(st.session_state["cronograma_linha_do_dia"])

    if st.session_state["cron_materia"].strip():
        st.session_state["mat_did"] = st.session_state["cron_materia"].strip()

    st.session_state["config_area_materia"] = st.session_state["cron_area_materia"]
    st.session_state["config_hoje"] = st.session_state["cron_hoje"]
    st.session_state["config_prova"] = st.session_state["cron_prova"]

    st.session_state["conteudo_dia"] = (
        campos["texto_colar"]
        or campos["conteudo"]
        or st.session_state["cronograma_linha_do_dia"].strip()
    )

    if campos["objetivo"]:
        st.session_state["objetivo_dia"] = campos["objetivo"]

    set_msg(
        "Matéria, conteúdo do dia, objetivo e datas foram enviados para Configuração.",
        "success",
    )


# =====================================================
# Sidebar
# =====================================================

with st.sidebar:
    st.markdown("## Etapas")

    idx = STEPS.index(st.session_state["current_step"])
    st.progress((idx + 1) / len(STEPS))
    st.caption(f"Etapa {idx+1} de {len(STEPS)}")

    for step_name in STEPS:
        emoji = "👉 " if step_name == st.session_state["current_step"] else ""
        if st.button(f"{emoji}{step_name}", use_container_width=True, key=f"nav_{step_name}"):
            goto_step(step_name)

    st.markdown("---")
    st.markdown("## Perfis salvos")

    profiles = load_saved_profiles()
    st.session_state["saved_profiles"] = profiles
    saved_names = sorted(list(profiles.keys()))

    if not saved_names:
        st.caption("Nenhum perfil salvo.")
    else:
        selected_profile = st.selectbox(
            "Selecionar perfil",
            options=[""] + saved_names,
            key="perfil_sidebar_select",
        )

        c1, c2 = st.columns(2)

        with c1:
            if st.button("Carregar", use_container_width=True, key="sidebar_load_profile"):
                if selected_profile:
                    load_profile_from_disk(selected_profile)
                    set_msg(f"Perfil '{selected_profile}' carregado.", "success")
                    st.rerun()

        with c2:
            if st.button("Excluir", use_container_width=True, key="sidebar_delete_profile"):
                if selected_profile:
                    delete_profile_from_disk(selected_profile)
                    st.session_state["perfil_sidebar_select"] = ""
                    set_msg(f"Perfil '{selected_profile}' excluído.", "success")
                    st.rerun()

    st.markdown("---")
    st.session_state["mostrar_debug"] = st.checkbox(
        "Mostrar detalhes técnicos",
        value=st.session_state.get("mostrar_debug", False),
    )

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
    with c1:
        st.text_input("Nome", key="nome")
        st.text_input("Idade", key="idade")
        st.text_input("Escola", key="escola")

    with c2:
        st.text_input("Apelido", key="apelido")
        st.text_input("Série / Ano", key="serie")
        st.text_input("Turno", key="turno")

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
    with c1:
        st.text_input("Nome para salvar", key="novo_nome_perfil")
    with c2:
        if st.button("Salvar", key="save_profile_btn"):
            nome = st.session_state["novo_nome_perfil"].strip()
            if nome:
                save_profile_to_disk(nome)
                set_msg(f"Perfil '{nome}' salvo.", "success")
                st.rerun()

    footer_nav()

# =====================================================
# APRENDIZAGEM
# =====================================================

elif step == "Aprendizagem":
    st.subheader("Perfil de aprendizagem")

    st.radio("Atenção sustentada", ATENCAO_OPTIONS, key="atencao_sustentada", horizontal=True)
    st.radio("Autonomia", AUTONOMIA_OPTIONS, key="autonomia", horizontal=True)
    st.radio("Canal preferencial", CANAL_OPTIONS, key="canal_preferencial", horizontal=True)
    st.radio("Tolerância à frustração", FRUSTRACAO_OPTIONS, key="tolerancia_frustracao", horizontal=True)
    st.radio("Leitura", NIVEL_OPTIONS, key="leitura_nivel", horizontal=True)
    st.radio("Escrita", NIVEL_OPTIONS, key="escrita_nivel", horizontal=True)
    st.radio("Matemática", NIVEL_OPTIONS, key="matematica_nivel", horizontal=True)
    st.radio("Compreensão oral", ["Baixa", "Média", "Boa"], key="compreensao_oral", horizontal=True)

    st.markdown("### Erros e dificuldades")

    checkbox_group("Tipo de erro mais comum", ERRO_OPTIONS, "tipo_erro_mais_comum", 3)
    if "Outro" in st.session_state["tipo_erro_mais_comum"]:
        st.text_input("Outro tipo de erro", key="tipo_erro_outro")

    checkbox_group("O que mais engaja", ENGAJAMENTO_OPTIONS, "engajamento", 3)
    if "Outro" in st.session_state["engajamento"]:
        st.text_input("Outro engajamento", key="engajamento_outro")

    checkbox_group("Principal dificuldade", DIFICULDADE_OPTIONS, "principal_dificuldade", 3)
    if "Outro" in st.session_state["principal_dificuldade"]:
        st.text_input("Outra dificuldade", key="dificuldade_outro")

    checkbox_group("Sinais quando trava", TRAVA_OPTIONS, "sinais_quando_trava", 3)
    if "Outro" in st.session_state["sinais_quando_trava"]:
        st.text_input("Outro sinal", key="trava_outro")

    checkbox_group("Melhor forma de retomar", RETOMADA_OPTIONS, "melhor_forma_retomar", 3)
    if "Outro" in st.session_state["melhor_forma_retomar"]:
        st.text_input("Outra forma de retomar", key="retomada_outro")

    footer_nav()

# =====================================================
# CRONOGRAMA
# =====================================================

elif step == "Cronograma":
    st.subheader("Cronograma até a prova")

    st.text_input("Matéria", key="cron_materia")
    st.selectbox("Área da matéria", AREA_MATERIA_OPTIONS, key="cron_area_materia")

    hoje = st.date_input("Hoje", value=st.session_state.get("cron_hoje", datetime.date.today()), key="cron_hoje")
    prova = st.date_input("Prova", value=st.session_state.get("cron_prova", datetime.date.today()), key="cron_prova")

    st.caption(f"Hoje: {formatar_data_br(hoje)}")
    st.caption(f"Data da prova: {formatar_data_br(prova)}")

    st.text_area("Conteúdos da prova", key="cron_conteudos", height=120)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.text_area("Alta prioridade", key="cron_alta", height=120)
    with c2:
        st.text_area("Média prioridade", key="cron_media", height=120)
    with c3:
        st.text_area("Baixa prioridade", key="cron_baixa", height=120)

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

    if st.session_state["mostrar_debug"]:
        with st.expander("Detalhes técnicos do cronograma"):
            st.code(json.dumps(perfil, ensure_ascii=False, indent=2), language="json")

    with st.expander("Prompt de cronograma"):
        show_prompt_block("Prompt Cronograma", txt, "cronograma")

    st.markdown("### Usar linha do cronograma")
    st.text_area("Cole aqui a linha do dia", key="cronograma_linha_do_dia", height=90)

    if st.button("Usar esta linha na Configuração"):
        apply_cronograma_to_config()
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

    hoje = st.date_input("Hoje", value=st.session_state.get("config_hoje", datetime.date.today()), key="config_hoje")
    prova = st.date_input("Prova", value=st.session_state.get("config_prova", datetime.date.today()), key="config_prova")

    st.caption(f"Hoje: {formatar_data_br(hoje)}")
    st.caption(f"Data da prova: {formatar_data_br(prova)}")

    st.radio("Situação", SITUACAO_OPTIONS, key="situacao_conteudo", horizontal=True)
    st.radio("Prioridade", PRIORIDADE_OPTIONS, key="prioridade_conteudo", horizontal=True)

    st.toggle("Usar anexos apenas como embasamento", key="usa_fontes")

    st.markdown("### Como a escola cobra")
    checkbox_group(
        "Selecione os formatos mais comuns",
        ESCOLA_COBRANCA_OPTIONS,
        "cobranca_escola",
        3
    )
    if "Outro" in st.session_state["cobranca_escola"]:
        st.text_input("Outro tipo de cobrança", key="cobranca_extra")

    st.markdown("### Materiais")
    checkbox_group(
        "Materiais",
        ["Vídeo", "Áudio (responsável)", "Slides", "Flashcards (máx 10)", "Teste"],
        "selected_materials",
        3
    )

    if st.session_state["mostrar_debug"]:
        perfil = get_profile_base(prova)
        with st.expander("Detalhes técnicos da configuração"):
            st.code(json.dumps(perfil, ensure_ascii=False, indent=2), language="json")

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

    if st.session_state["mostrar_debug"]:
        with st.expander("Detalhes técnicos do Studio"):
            st.code(json.dumps(perfil, ensure_ascii=False, indent=2), language="json")

    tabs = st.tabs(["Vídeo", "Áudio", "Slides", "Flashcards", "Teste"])

    with tabs[0]:
        video_prompt = prompt_video(
            perfil, materia, area, conteudo, objetivo,
            estilo, situacao, prioridade, days,
            usa, resumo_aluno_compacto
        )
        show_prompt_block("Prompt Vídeo", video_prompt, "video")

    with tabs[1]:
        audio_prompt = prompt_audio(
            perfil, materia, area, conteudo, objetivo,
            estilo, situacao, prioridade, days,
            usa, resumo_aluno_compacto
        )
        show_prompt_block("Prompt Áudio", audio_prompt, "audio")

    with tabs[2]:
        slides_prompt = prompt_slides(
            perfil, materia, area, conteudo, objetivo,
            estilo, situacao, prioridade, days,
            usa, resumo_aluno_compacto
        )
        show_prompt_block("Prompt Slides", slides_prompt, "slides")

    with tabs[3]:
        flash_prompt = prompt_flash(
            perfil, materia, area, conteudo, objetivo,
            estilo, situacao, prioridade, days,
            usa, resumo_aluno_compacto
        )
        show_prompt_block("Prompt Flashcards", flash_prompt, "flashcards")

    with tabs[4]:
        teste_prompt = prompt_teste(
            perfil, materia, area, conteudo, objetivo,
            estilo, situacao, prioridade, days,
            usa, resumo_aluno_compacto
        )
        show_prompt_block("Prompt Teste", teste_prompt, "teste")

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
    show_prompt_block("Pacote completo", aula, "aula_completa")

    footer_nav()
