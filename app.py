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

st.set_page_config(page_title="EduAI Studio", page_icon="🧠", layout="wide")

init_state()
migrate_legacy_keys()
inject_styles()

st.session_state.setdefault("current_step", "Perfil")
st.session_state.setdefault("saved_profiles", {})
st.session_state.setdefault("novo_nome_perfil", "")
st.session_state.setdefault("nav_message", "")
st.session_state.setdefault("nav_message_type", "info")
st.session_state.setdefault("cron_area_materia", "")
st.session_state.setdefault("config_area_materia", "")


TEXT_STORAGE_KEYS = [
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


def widget_key(storage_key: str) -> str:
    return f"_w_{storage_key}"


def sync_storage_to_widget(storage_key: str):
    wk = widget_key(storage_key)
    if wk not in st.session_state:
        st.session_state[wk] = st.session_state.get(storage_key, "")


def sync_widget_to_storage(storage_key: str):
    wk = widget_key(storage_key)
    st.session_state[storage_key] = st.session_state.get(wk, "")


def persist_all_text_widgets():
    for key in TEXT_STORAGE_KEYS:
        wk = widget_key(key)
        if wk in st.session_state:
            st.session_state[key] = st.session_state[wk]


def persistent_text_input(label: str, storage_key: str, **kwargs):
    sync_storage_to_widget(storage_key)
    return st.text_input(
        label,
        key=widget_key(storage_key),
        on_change=sync_widget_to_storage,
        args=(storage_key,),
        **kwargs,
    )


def persistent_text_area(label: str, storage_key: str, **kwargs):
    sync_storage_to_widget(storage_key)
    return st.text_area(
        label,
        key=widget_key(storage_key),
        on_change=sync_widget_to_storage,
        args=(storage_key,),
        **kwargs,
    )


def persistent_selectbox(label: str, options, storage_key: str, **kwargs):
    st.session_state.setdefault(storage_key, options[0] if options else "")
    wk = widget_key(storage_key)
    if wk not in st.session_state:
        st.session_state[wk] = st.session_state[storage_key]

    def _sync():
        st.session_state[storage_key] = st.session_state[wk]

    return st.selectbox(
        label,
        options,
        key=wk,
        on_change=_sync,
        **kwargs,
    )


def persistent_date_input(label: str, storage_key: str, default_value=None, **kwargs):
    if default_value is None:
        default_value = datetime.date.today()

    st.session_state.setdefault(storage_key, default_value)
    wk = widget_key(storage_key)
    if wk not in st.session_state:
        st.session_state[wk] = st.session_state[storage_key]

    def _sync():
        st.session_state[storage_key] = st.session_state[wk]

    return st.date_input(
        label,
        key=wk,
        on_change=_sync,
        **kwargs,
    )


def persistent_toggle(label: str, storage_key: str, **kwargs):
    st.session_state.setdefault(storage_key, False)
    wk = widget_key(storage_key)
    if wk not in st.session_state:
        st.session_state[wk] = st.session_state[storage_key]

    def _sync():
        st.session_state[storage_key] = st.session_state[wk]

    return st.toggle(
        label,
        key=wk,
        on_change=_sync,
        **kwargs,
    )


def set_nav_message(msg: str, msg_type: str = "warning"):
    st.session_state["nav_message"] = msg
    st.session_state["nav_message_type"] = msg_type


def clear_nav_message():
    st.session_state["nav_message"] = ""
    st.session_state["nav_message_type"] = "info"


def sync_checkbox_group_keys(state_key, options):
    selected = set(st.session_state.get(state_key, []))
    for option in options:
        wkey = f"{state_key}_{slugify(option)}"
        st.session_state[wkey] = option in selected


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

    for key in TEXT_STORAGE_KEYS:
        wk = widget_key(key)
        if wk in st.session_state:
            del st.session_state[wk]


def get_profile_base(date_obj=None):
    persist_all_text_widgets()
    if date_obj is None:
        date_obj = datetime.date.today()
    atualizar_caracteristicas_sugeridas()
    return get_perfil_data(formatar_data_br(date_obj))


def validate_step(step_name: str):
    persist_all_text_widgets()
    erros = []

    if step_name == "Perfil":
        if not st.session_state.get("nome", "").strip():
            erros.append("Preencha o nome do aluno.")
        if not st.session_state.get("idade", "").strip():
            erros.append("Preencha a idade do aluno.")
        if not st.session_state.get("serie", "").strip():
            erros.append("Preencha a série/ano do aluno.")

    elif step_name == "Aprendizagem":
        if not st.session_state.get("engajamento", []):
            erros.append("Selecione ao menos uma opção em 'O que mais engaja'.")
        if not st.session_state.get("principal_dificuldade", []):
            erros.append("Selecione ao menos uma opção em 'Principal dificuldade'.")
        if not st.session_state.get("melhor_forma_retomar", []):
            erros.append("Selecione ao menos uma opção em 'Melhor forma de retomar'.")

    elif step_name == "Cronograma":
        if not st.session_state.get("cron_materia", "").strip():
            erros.append("Preencha a matéria do cronograma.")
        if not st.session_state.get("cron_conteudos", "").strip():
            erros.append("Preencha os conteúdos da prova.")
        hoje = st.session_state.get("cron_hoje_input", datetime.date.today())
        prova = st.session_state.get("cron_prova_input", datetime.date.today())
        if hoje and prova and prova < hoje:
            erros.append("A data da prova não pode ser anterior à data de hoje.")

    elif step_name == "Configuração":
        if not st.session_state.get("mat_did", "").strip():
            erros.append("Preencha a matéria na Configuração.")
        if not st.session_state.get("conteudo_dia", "").strip():
            erros.append("Preencha o conteúdo do dia.")
        if not st.session_state.get("selected_materials", []):
            erros.append("Selecione ao menos um material.")

    return erros


def set_step(step_name: str):
    persist_all_text_widgets()
    erros = validate_step(st.session_state["current_step"])

    if erros and step_name != st.session_state["current_step"]:
        set_nav_message(
            "⚠️ Alguns campos ainda não foram preenchidos:\n- " + "\n- ".join(erros),
            "warning",
        )
    else:
        clear_nav_message()

    st.session_state["current_step"] = step_name


def go_next():
    persist_all_text_widgets()
    idx = STEPS.index(st.session_state["current_step"])
    if idx < len(STEPS) - 1:
        set_step(STEPS[idx + 1])


def go_prev():
    persist_all_text_widgets()
    idx = STEPS.index(st.session_state["current_step"])
    if idx > 0:
        clear_nav_message()
        st.session_state["current_step"] = STEPS[idx - 1]


def get_step_status(step_name: str):
    errors = validate_step(step_name)
    return len(errors) == 0, errors


def apply_cronograma_to_config():
    persist_all_text_widgets()
    campos = extrair_campos_cronograma(st.session_state["cronograma_linha_do_dia"])

    if st.session_state["cron_materia"].strip():
        st.session_state["mat_did"] = st.session_state["cron_materia"].strip()

    st.session_state["config_area_materia"] = st.session_state["cron_area_materia"]

    st.session_state["conteudo_dia"] = (
        campos["texto_colar"]
        or campos["conteudo"]
        or st.session_state["cronograma_linha_do_dia"].strip()
    )

    if campos["objetivo"]:
        st.session_state["objetivo_dia"] = campos["objetivo"]

    set_nav_message(
        "Matéria, conteúdo do dia e objetivo foram enviados para Configuração.",
        "success",
    )


def render_sidebar_navigation():
    with st.sidebar:
        st.markdown("## Etapas")
        current_idx = STEPS.index(st.session_state["current_step"])
        st.progress((current_idx + 1) / len(STEPS))
        st.caption(f"Etapa {current_idx + 1} de {len(STEPS)}")

        for i, step_name in enumerate(STEPS):
            prefix = "👉 " if step_name == st.session_state["current_step"] else ""
            st.button(
                f"{prefix}{step_name}",
                key=f"side_step_btn_{i}",
                use_container_width=True,
                on_click=set_step,
                args=(step_name,),
            )

        st.markdown("### Checklist da etapa atual")
        ok, errors = get_step_status(st.session_state["current_step"])
        if ok:
            st.success("Etapa preenchida o suficiente para seguir.")
        else:
            for err in errors:
                st.caption(f"• {err}")


def render_step_footer():
    idx = STEPS.index(st.session_state["current_step"])
    c1, c2, _ = st.columns([1, 1, 4])

    with c1:
        if idx > 0:
            st.button(
                "⬅ Etapa anterior",
                key=f"footer_prev_{idx}",
                on_click=go_prev,
            )

    with c2:
        if idx < len(STEPS) - 1:
            st.button(
                "Próxima etapa ➜",
                key=f"footer_next_{idx}",
                on_click=go_next,
            )


st.title("🧠 EduAI Studio - pacote revisado")
st.caption("Navegação estável, perfil consolidado nos prompts e materiais autossuficientes.")

render_sidebar_navigation()

if st.session_state["nav_message"]:
    if st.session_state["nav_message_type"] == "warning":
        st.warning(st.session_state["nav_message"])
    elif st.session_state["nav_message_type"] == "success":
        st.success(st.session_state["nav_message"])
    else:
        st.info(st.session_state["nav_message"])

step = st.session_state["current_step"]

if step == "Perfil":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Conhecendo a criança")
    c1, c2 = st.columns(2)

    with c1:
        persistent_text_input("Nome", "nome")
        persistent_text_input("Idade", "idade")
        persistent_text_input("Escola", "escola")

    with c2:
        persistent_text_input("Apelido", "apelido")
        persistent_text_input("Série / Ano", "serie")
        persistent_text_input("Turno", "turno")

    persistent_text_input("Nome do responsável", "responsavel")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Interesses")
    checkbox_group("Selecione os interesses da criança", INTERESSES_OPTIONS, "interesses", columns=4)
    if "Outro" in st.session_state["interesses"]:
        persistent_text_input("Outro interesse", "interesses_outro")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Diagnósticos e características")
    checkbox_group("Selecione um ou mais diagnósticos", DIAG_OPTIONS, "diagnosticos", columns=3)

    if "Outro" in st.session_state["diagnosticos"]:
        persistent_text_input("Qual outro diagnóstico?", "outro_diagnostico")

    atualizar_caracteristicas_sugeridas()

    st.text_area(
        "Características sugeridas automaticamente pelos diagnósticos",
        value=st.session_state.get("caracteristicas_sugeridas", ""),
        height=120,
        disabled=True,
    )

    persistent_text_area(
        "Outras características (editável)",
        "outras_caracteristicas",
        height=120,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Salvar ou carregar perfil do aluno")
    c1, c2 = st.columns([2, 1])

    with c1:
        persistent_text_input(
            "Nome para salvar este perfil",
            "novo_nome_perfil",
            placeholder="Ex: Filho 1, Gustavo, Aluna Ana",
        )

    with c2:
        if st.button("Salvar perfil", key="salvar_perfil_btn"):
            persist_all_text_widgets()
            atualizar_caracteristicas_sugeridas()
            nome_salvar = st.session_state["novo_nome_perfil"].strip()
            if nome_salvar:
                save_named_profile(nome_salvar)
            set_nav_message("Perfil salvo com sucesso.", "success")
            st.rerun()

    perfis_salvos = list(st.session_state["saved_profiles"].keys())
    if perfis_salvos:
        perfil_escolhido = st.selectbox(
            "Perfis salvos",
            [""] + perfis_salvos,
            key="perfil_salvo_select",
        )
        if st.button("Carregar perfil salvo", key="carregar_perfil_btn"):
            if perfil_escolhido:
                load_named_profile(perfil_escolhido)
                sync_all_checkbox_groups()
                atualizar_caracteristicas_sugeridas()
                set_nav_message(f"Perfil '{perfil_escolhido}' carregado.", "success")
                st.rerun()

    if st.button("Salvar e ir para Aprendizagem", key="salvar_ir_aprendizagem_btn"):
        persist_all_text_widgets()
        atualizar_caracteristicas_sugeridas()
        nome_salvar = st.session_state["novo_nome_perfil"].strip()
        if nome_salvar:
            save_named_profile(nome_salvar)
        clear_nav_message()
        st.session_state["current_step"] = "Aprendizagem"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    render_step_footer()

elif step == "Aprendizagem":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Perfil de aprendizagem")

    radio_group("Atenção sustentada", ATENCAO_OPTIONS, "atencao_sustentada", horizontal=True)
    radio_group("Autonomia", AUTONOMIA_OPTIONS, "autonomia", horizontal=True)
    radio_group("Canal preferencial", CANAL_OPTIONS, "canal_preferencial", horizontal=True)
    radio_group("Tolerância à frustração", FRUSTRACAO_OPTIONS, "tolerancia_frustracao", horizontal=True)
    radio_group("Leitura", NIVEL_OPTIONS, "leitura_nivel", horizontal=True)
    radio_group("Escrita", NIVEL_OPTIONS, "escrita_nivel", horizontal=True)
    radio_group("Matemática", NIVEL_OPTIONS, "matematica_nivel", horizontal=True)
    radio_group("Compreensão oral", ["Baixa", "Média", "Boa"], "compreensao_oral", horizontal=True)

    checkbox_group("Tipo de erro mais comum", ERRO_OPTIONS, "tipo_erro_mais_comum", columns=3)
    if "Outro" in st.session_state["tipo_erro_mais_comum"]:
        persistent_text_input("Descreva o tipo de erro mais comum", "tipo_erro_outro")

    st.markdown("<hr>", unsafe_allow_html=True)

    checkbox_group("O que mais engaja", ENGAJAMENTO_OPTIONS, "engajamento", columns=3)
    if "Outro" in st.session_state["engajamento"]:
        persistent_text_input("Outro fator de engajamento", "engajamento_outro")

    checkbox_group("Principal dificuldade", DIFICULDADE_OPTIONS, "principal_dificuldade", columns=3)
    if "Outro" in st.session_state["principal_dificuldade"]:
        persistent_text_input("Outra dificuldade observada", "dificuldade_outro")

    checkbox_group("Sinais quando trava", TRAVA_OPTIONS, "sinais_quando_trava", columns=3)
    if "Outro" in st.session_state["sinais_quando_trava"]:
        persistent_text_input("Outro sinal quando trava", "trava_outro")

    checkbox_group("Melhor forma de retomar", RETOMADA_OPTIONS, "melhor_forma_retomar", columns=3)
    if "Outro" in st.session_state["melhor_forma_retomar"]:
        persistent_text_input("Outra forma de retomar", "retomada_outro")

    render_step_footer()
    st.markdown("</div>", unsafe_allow_html=True)

elif step == "Cronograma":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Plano de estudo até a prova")

    persistent_text_input("Matéria", "cron_materia")
    persistent_selectbox("Área da matéria (opcional)", AREA_MATERIA_OPTIONS, "cron_area_materia")

    hoje = persistent_date_input("Data de hoje", "cron_hoje_input", default_value=datetime.date.today())
    prova = persistent_date_input("Data da prova", "cron_prova_input", default_value=datetime.date.today())

    perfil = get_profile_base(prova)

    st.text_area(
        "Perfil consolidado usado no cronograma",
        value=json.dumps(perfil, ensure_ascii=False, indent=2),
        height=220,
    )

    persistent_text_area("Conteúdos da prova", "cron_conteudos", height=120)

    a1, a2, a3 = st.columns(3)
    with a1:
        persistent_text_area("Prioridade alta", "cron_alta", height=110)
    with a2:
        persistent_text_area("Prioridade média", "cron_media", height=110)
    with a3:
        persistent_text_area("Prioridade baixa", "cron_baixa", height=110)

    txt_cron = prompt_cronograma(
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

    st.text_area("Prompt de cronograma", value=txt_cron, height=380)
    persistent_text_area("Cole aqui a linha do dia gerada no cronograma", "cronograma_linha_do_dia", height=90)

    c1, c2 = st.columns(2)
    if c1.button("Salvar cronograma", key="salvar_cronograma_btn"):
        persist_all_text_widgets()
        set_nav_message("Cronograma salvo.", "success")
        st.rerun()

    if c2.button("Usar essa linha na Configuração", key="cron_usar_linha_btn"):
        persist_all_text_widgets()
        apply_cronograma_to_config()
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    render_step_footer()

elif step == "Configuração":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Configuração didática do dia")

    persistent_text_input("Matéria", "mat_did")
    persistent_selectbox("Área da matéria (opcional)", AREA_MATERIA_OPTIONS, "config_area_materia")
    persistent_text_area("Conteúdo do dia", "conteudo_dia", height=120)
    persistent_text_input("Objetivo do dia (opcional)", "objetivo_dia")

    hoje2 = persistent_date_input("Data de hoje", "config_did_hoje", default_value=datetime.date.today())
    prova2 = persistent_date_input("Data da prova", "config_did_prova", default_value=datetime.date.today())

    radio_group("Situação do conteúdo", SITUACAO_OPTIONS, "situacao_conteudo", horizontal=True)
    radio_group("Prioridade do conteúdo", PRIORIDADE_OPTIONS, "prioridade_conteudo", horizontal=True)

    persistent_toggle("Usar com fontes anexadas no NotebookLM", "usa_fontes")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Como a escola cobra")
    checkbox_group("Selecione os formatos mais comuns", ESCOLA_COBRANCA_OPTIONS, "cobranca_escola", columns=3)
    if "Outro" in st.session_state["cobranca_escola"]:
        persistent_text_input("Outro tipo de cobrança", "cobranca_extra")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Materiais")
    checkbox_group(
        "Escolha os materiais",
        ["Vídeo", "Áudio (responsável)", "Slides", "Flashcards (máx 10)", "Teste"],
        "selected_materials",
        columns=3,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    perfil_config = get_profile_base(prova2)
    st.text_area(
        "Perfil consolidado usado na configuração",
        value=json.dumps(perfil_config, ensure_ascii=False, indent=2),
        height=260,
    )

    render_step_footer()

elif step == "Studio":
    try:
        hoje2 = st.session_state["config_did_hoje"]
        prova2 = st.session_state["config_did_prova"]
        days = (prova2 - hoje2).days
        estilo = obter_cobranca()
    except Exception:
        days = 0
        estilo = ""
        prova2 = datetime.date.today()

    perfil = get_profile_base(prova2)
    usa = st.session_state["usa_fontes"]
    materia = st.session_state["mat_did"]
    area = st.session_state["config_area_materia"]
    conteudo = st.session_state["conteudo_dia"]
    objetivo = st.session_state["objetivo_dia"]
    situacao = st.session_state["situacao_conteudo"]
    prioridade = st.session_state["prioridade_conteudo"]

    st.text_area(
        "Perfil consolidado usado nos prompts",
        value=json.dumps(perfil, ensure_ascii=False, indent=2),
        height=260,
    )

    base_prompt_studio = contexto_studio_compacto(
        perfil, materia, area, conteudo, objetivo, estilo, situacao, prioridade, days, usa, resumo_aluno_compacto
    )
    st.text_area("Base real enviada para os prompts", value=base_prompt_studio, height=360)

    c1, c2 = st.columns(2)

    with c1:
        st.text_area(
            "Prompt de vídeo",
            value=prompt_video(perfil, materia, area, conteudo, objetivo, estilo, situacao, prioridade, days, usa, resumo_aluno_compacto),
            height=230,
        )
        st.text_area(
            "Prompt de slides",
            value=prompt_slides(perfil, materia, area, conteudo, objetivo, estilo, situacao, prioridade, days, usa, resumo_aluno_compacto),
            height=230,
        )
        st.text_area(
            "Prompt de flashcards",
            value=prompt_flash(perfil, materia, area, conteudo, objetivo, estilo, situacao, prioridade, days, usa, resumo_aluno_compacto),
            height=230,
        )

    with c2:
        st.text_area(
            "Prompt de áudio",
            value=prompt_audio(perfil, materia, area, conteudo, objetivo, estilo, situacao, prioridade, days, usa, resumo_aluno_compacto),
            height=250,
        )
        st.text_area(
            "Prompt de teste",
            value=prompt_teste(perfil, materia, area, conteudo, objetivo, estilo, situacao, prioridade, days, usa, resumo_aluno_compacto),
            height=230,
        )

    render_step_footer()

elif step == "Aula Completa":
    try:
        hoje2 = st.session_state["config_did_hoje"]
        prova2 = st.session_state["config_did_prova"]
        days = (prova2 - hoje2).days
        estilo = obter_cobranca()
    except Exception:
        days = 0
        estilo = ""
        prova2 = datetime.date.today()

    perfil = get_profile_base(prova2)

    aula = prompt_aula(
        perfil,
        st.session_state["mat_did"],
        st.session_state["config_area_materia"],
        st.session_state["conteudo_dia"],
        st.session_state["objetivo_dia"],
        estilo,
        st.session_state["situacao_conteudo"],
        st.session_state["prioridade_conteudo"],
        days,
        st.session_state["selected_materials"],
        st.session_state["usa_fontes"],
        modo_estudo,
    )

    st.text_area("Aula completa", value=aula, height=420)
    render_step_footer()
