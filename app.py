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
from ui_components import inject_styles, checkbox_group, slugify
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

# Carrega perfis persistidos uma vez
if not st.session_state["saved_profiles"]:
    st.session_state["saved_profiles"] = load_saved_profiles()

# =====================================================
# Persistência de widgets
# =====================================================

PERSISTENT_TEXT_KEYS = [
    "nome",
    "apelido",
    "idade",
    "serie",
    "escola",
    "turno",
    "responsavel",
    "interesses_outro",
    "outro_diagnostico",
    "outras_caracteristicas",
    "novo_nome_perfil",
    "tipo_erro_outro",
    "engajamento_outro",
    "dificuldade_outro",
    "trava_outro",
    "retomada_outro",
    "cron_materia",
    "cron_conteudos",
    "cron_alta",
    "cron_media",
    "cron_baixa",
    "cronograma_linha_do_dia",
    "mat_did",
    "conteudo_dia",
    "objetivo_dia",
    "cobranca_extra",
]

PERSISTENT_SELECT_KEYS = [
    "cron_area_materia",
    "config_area_materia",
]

PERSISTENT_DATE_KEYS = [
    "cron_hoje",
    "cron_prova",
    "config_hoje",
    "config_prova",
]

PERSISTENT_BOOL_KEYS = [
    "usa_fontes",
]

PERSISTENT_RADIO_KEYS = [
    "atencao_sustentada",
    "autonomia",
    "canal_preferencial",
    "tolerancia_frustracao",
    "leitura_nivel",
    "escrita_nivel",
    "matematica_nivel",
    "compreensao_oral",
    "situacao_conteudo",
    "prioridade_conteudo",
]


def _wk(storage_key: str) -> str:
    return f"_w_{storage_key}"


def init_widget_from_storage(storage_key: str, default=""):
    wk = _wk(storage_key)
    if storage_key not in st.session_state:
        st.session_state[storage_key] = default
    if wk not in st.session_state:
        st.session_state[wk] = st.session_state[storage_key]


def sync_widget_to_storage(storage_key: str):
    st.session_state[storage_key] = st.session_state.get(_wk(storage_key))


def sync_storage_to_widget(storage_key: str):
    st.session_state[_wk(storage_key)] = st.session_state.get(storage_key)


def persist_all_widgets():
    for k in (
        PERSISTENT_TEXT_KEYS
        + PERSISTENT_SELECT_KEYS
        + PERSISTENT_DATE_KEYS
        + PERSISTENT_BOOL_KEYS
        + PERSISTENT_RADIO_KEYS
    ):
        wk = _wk(k)
        if wk in st.session_state:
            st.session_state[k] = st.session_state[wk]


def persistent_text_input(label: str, storage_key: str, **kwargs):
    init_widget_from_storage(storage_key, "")
    return st.text_input(
        label,
        key=_wk(storage_key),
        on_change=sync_widget_to_storage,
        args=(storage_key,),
        **kwargs,
    )


def persistent_text_area(label: str, storage_key: str, **kwargs):
    init_widget_from_storage(storage_key, "")
    return st.text_area(
        label,
        key=_wk(storage_key),
        on_change=sync_widget_to_storage,
        args=(storage_key,),
        **kwargs,
    )


def persistent_selectbox(label: str, options, storage_key: str, **kwargs):
    default = options[0] if options else ""
    init_widget_from_storage(storage_key, default)

    def _sync():
        sync_widget_to_storage(storage_key)

    return st.selectbox(
        label,
        options,
        key=_wk(storage_key),
        on_change=_sync,
        **kwargs,
    )


def persistent_date_input(label: str, storage_key: str, default_value=None, **kwargs):
    if default_value is None:
        default_value = datetime.date.today()
    init_widget_from_storage(storage_key, default_value)

    def _sync():
        sync_widget_to_storage(storage_key)

    return st.date_input(
        label,
        key=_wk(storage_key),
        on_change=_sync,
        **kwargs,
    )


def persistent_toggle(label: str, storage_key: str, **kwargs):
    init_widget_from_storage(storage_key, False)

    def _sync():
        sync_widget_to_storage(storage_key)

    return st.toggle(
        label,
        key=_wk(storage_key),
        on_change=_sync,
        **kwargs,
    )


def persistent_radio(label: str, options, storage_key: str, horizontal=False):
    default = options[0] if options else ""
    init_widget_from_storage(storage_key, default)

    valor_atual = st.session_state.get(_wk(storage_key), default)
    if valor_atual not in options:
        valor_atual = default
        st.session_state[_wk(storage_key)] = default
        st.session_state[storage_key] = default

    def _sync():
        sync_widget_to_storage(storage_key)

    return st.radio(
        label,
        options,
        index=options.index(valor_atual),
        horizontal=horizontal,
        key=_wk(storage_key),
        on_change=_sync,
    )

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
    persist_all_widgets()
    st.session_state["current_step"] = step
    st.rerun()


def next_step():
    persist_all_widgets()
    idx = STEPS.index(st.session_state["current_step"])
    if idx < len(STEPS) - 1:
        goto_step(STEPS[idx + 1])


def prev_step():
    persist_all_widgets()
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
    persist_all_widgets()
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
        ["Vídeo", "Áudio (responsável)", "Slides", "Flashcards (máx 10)", "Teste"],
    )

    for k in (
        PERSISTENT_TEXT_KEYS
        + PERSISTENT_SELECT_KEYS
        + PERSISTENT_DATE_KEYS
        + PERSISTENT_BOOL_KEYS
        + PERSISTENT_RADIO_KEYS
    ):
        sync_storage_to_widget(k)


def collect_profile_payload():
    persist_all_widgets()
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
    sync_all_checkbox_groups()
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


def apply_cronograma_to_config():
    persist_all_widgets()
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

    sync_storage_to_widget("mat_did")
    sync_storage_to_widget("config_area_materia")
    sync_storage_to_widget("config_hoje")
    sync_storage_to_widget("config_prova")
    sync_storage_to_widget("conteudo_dia")
    sync_storage_to_widget("objetivo_dia")

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

    saved = list(load_saved_profiles().keys())
    st.session_state["saved_profiles"] = load_saved_profiles()

    if not saved:
        st.caption("Nenhum perfil salvo.")
    else:
        for p in saved:
            if st.button(p, use_container_width=True, key=f"profile_{p}"):
                load_profile_from_disk(p)
                set_msg(f"Perfil '{p}' carregado.", "success")
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
        persistent_text_input("Nome", "nome")
        persistent_text_input("Idade", "idade")
        persistent_text_input("Escola", "escola")

    with c2:
        persistent_text_input("Apelido", "apelido")
        persistent_text_input("Série / Ano", "serie")
        persistent_text_input("Turno", "turno")

    persistent_text_input("Responsável", "responsavel")

    st.markdown("### Interesses")
    checkbox_group(
        "Selecione os interesses",
        INTERESSES_OPTIONS,
        "interesses",
        columns=4
    )

    if "Outro" in st.session_state["interesses"]:
        persistent_text_input("Outro interesse", "interesses_outro")

    st.markdown("### Diagnósticos")
    checkbox_group(
        "Selecione diagnósticos",
        DIAG_OPTIONS,
        "diagnosticos",
        columns=3
    )

    if "Outro" in st.session_state["diagnosticos"]:
        persistent_text_input("Outro diagnóstico", "outro_diagnostico")

    atualizar_caracteristicas_sugeridas()

    st.text_area(
        "Características sugeridas automaticamente",
        value=st.session_state["caracteristicas_sugeridas"],
        height=140,
        disabled=True
    )

    persistent_text_area(
        "Outras características",
        "outras_caracteristicas",
        height=120
    )

    st.markdown("### Salvar perfil")

    c1, c2 = st.columns([3, 1])
    with c1:
        persistent_text_input("Nome para salvar", "novo_nome_perfil")
    with c2:
        if st.button("Salvar", key="save_profile_btn"):
            persist_all_widgets()
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

    persistent_radio("Atenção sustentada", ATENCAO_OPTIONS, "atencao_sustentada", True)
    persistent_radio("Autonomia", AUTONOMIA_OPTIONS, "autonomia", True)
    persistent_radio("Canal preferencial", CANAL_OPTIONS, "canal_preferencial", True)
    persistent_radio("Tolerância à frustração", FRUSTRACAO_OPTIONS, "tolerancia_frustracao", True)
    persistent_radio("Leitura", NIVEL_OPTIONS, "leitura_nivel", True)
    persistent_radio("Escrita", NIVEL_OPTIONS, "escrita_nivel", True)
    persistent_radio("Matemática", NIVEL_OPTIONS, "matematica_nivel", True)
    persistent_radio("Compreensão oral", ["Baixa", "Média", "Boa"], "compreensao_oral", True)

    st.markdown("### Erros e dificuldades")

    checkbox_group("Tipo de erro mais comum", ERRO_OPTIONS, "tipo_erro_mais_comum", 3)
    if "Outro" in st.session_state["tipo_erro_mais_comum"]:
        persistent_text_input("Outro tipo de erro", "tipo_erro_outro")

    checkbox_group("O que mais engaja", ENGAJAMENTO_OPTIONS, "engajamento", 3)
    if "Outro" in st.session_state["engajamento"]:
        persistent_text_input("Outro engajamento", "engajamento_outro")

    checkbox_group("Principal dificuldade", DIFICULDADE_OPTIONS, "principal_dificuldade", 3)
    if "Outro" in st.session_state["principal_dificuldade"]:
        persistent_text_input("Outra dificuldade", "dificuldade_outro")

    checkbox_group("Sinais quando trava", TRAVA_OPTIONS, "sinais_quando_trava", 3)
    if "Outro" in st.session_state["sinais_quando_trava"]:
        persistent_text_input("Outro sinal", "trava_outro")

    checkbox_group("Melhor forma de retomar", RETOMADA_OPTIONS, "melhor_forma_retomar", 3)
    if "Outro" in st.session_state["melhor_forma_retomar"]:
        persistent_text_input("Outra forma de retomar", "retomada_outro")

    footer_nav()

# =====================================================
# CRONOGRAMA
# =====================================================

elif step == "Cronograma":
    st.subheader("Cronograma até a prova")

    persistent_text_input("Matéria", "cron_materia")
    persistent_selectbox("Área da matéria", AREA_MATERIA_OPTIONS, "cron_area_materia")

    hoje = persistent_date_input("Hoje", "cron_hoje", default_value=datetime.date.today())
    prova = persistent_date_input("Prova", "cron_prova", default_value=datetime.date.today())

    st.caption(f"Hoje: {formatar_data_br(hoje)}")
    st.caption(f"Data da prova: {formatar_data_br(prova)}")

    persistent_text_area("Conteúdos da prova", "cron_conteudos", height=120)

    c1, c2, c3 = st.columns(3)
    with c1:
        persistent_text_area("Alta prioridade", "cron_alta", height=120)
    with c2:
        persistent_text_area("Média prioridade", "cron_media", height=120)
    with c3:
        persistent_text_area("Baixa prioridade", "cron_baixa", height=120)

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
    persistent_text_area("Cole aqui a linha do dia", "cronograma_linha_do_dia", height=90)

    if st.button("Usar esta linha na Configuração"):
        apply_cronograma_to_config()
        goto_step("Configuração")

    footer_nav()

# =====================================================
# CONFIGURAÇÃO
# =====================================================

elif step == "Configuração":
    st.subheader("Configuração do estudo")

    persistent_text_input("Matéria", "mat_did")
    persistent_selectbox("Área da matéria", AREA_MATERIA_OPTIONS, "config_area_materia")

    persistent_text_area("Conteúdo do dia", "conteudo_dia", height=140)
    persistent_text_input("Objetivo do dia", "objetivo_dia")

    hoje = persistent_date_input("Hoje", "config_hoje", default_value=datetime.date.today())
    prova = persistent_date_input("Prova", "config_prova", default_value=datetime.date.today())

    st.caption(f"Hoje: {formatar_data_br(hoje)}")
    st.caption(f"Data da prova: {formatar_data_br(prova)}")

    persistent_radio("Situação", SITUACAO_OPTIONS, "situacao_conteudo", True)
    persistent_radio("Prioridade", PRIORIDADE_OPTIONS, "prioridade_conteudo", True)

    persistent_toggle("Usar anexos apenas como embasamento", "usa_fontes")

    st.markdown("### Como a escola cobra")
    checkbox_group(
        "Selecione os formatos mais comuns",
        ESCOLA_COBRANCA_OPTIONS,
        "cobranca_escola",
        3
    )
    if "Outro" in st.session_state["cobranca_escola"]:
        persistent_text_input("Outro tipo de cobrança", "cobranca_extra")

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
