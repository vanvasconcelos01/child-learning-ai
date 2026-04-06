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

st.set_page_config(page_title="EduAI Studio", page_icon="🧠", layout="wide")

init_state()
migrate_legacy_keys()
inject_styles()

# Compatibilidade extra caso constants.py ainda não tenha essas chaves novas
st.session_state.setdefault("current_step", "Perfil")
st.session_state.setdefault("saved_profiles", {})
st.session_state.setdefault("novo_nome_perfil", "")
st.session_state.setdefault("nav_message", "")
st.session_state.setdefault("nav_message_type", "info")
st.session_state.setdefault("cron_area_materia", "")
st.session_state.setdefault("config_area_materia", "")


def set_nav_message(msg: str, msg_type: str = "warning"):
    st.session_state["nav_message"] = msg
    st.session_state["nav_message_type"] = msg_type


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


def get_profile_base(date_obj=None):
    if date_obj is None:
        date_obj = datetime.date.today()
    atualizar_caracteristicas_sugeridas()
    return get_perfil_data(formatar_data_br(date_obj))


def profile_base_text(date_obj=None):
    return str(get_profile_base(date_obj))


def validate_step(step_name: str):
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
        hoje = st.session_state.get("cron_hoje_input")
        prova = st.session_state.get("cron_prova_input")
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


def can_go_to(target_step: str):
    current_idx = STEPS.index(st.session_state["current_step"])
    target_idx = STEPS.index(target_step)

    if target_idx <= current_idx:
        return True, []

    erros = validate_step(st.session_state["current_step"])
    return len(erros) == 0, erros


def goto_step(step_name: str):
    ok, erros = can_go_to(step_name)
    if ok:
        clear_nav_message()
        st.session_state["current_step"] = step_name
    else:
        set_nav_message("Antes de avançar:\n- " + "\n- ".join(erros), "warning")


def next_step():
    idx = STEPS.index(st.session_state["current_step"])
    if idx < len(STEPS) - 1:
        goto_step(STEPS[idx + 1])


def prev_step():
    idx = STEPS.index(st.session_state["current_step"])
    if idx > 0:
        clear_nav_message()
        st.session_state["current_step"] = STEPS[idx - 1]


def render_sidebar_navigation():
    with st.sidebar:
        st.markdown("## Etapas")
        current_idx = STEPS.index(st.session_state["current_step"])
        st.progress((current_idx + 1) / len(STEPS))
        st.caption(f"Etapa {current_idx + 1} de {len(STEPS)}")

        escolha = st.radio(
            "Ir para etapa",
            STEPS,
            index=current_idx,
            key="sidebar_step_radio"
        )

        if escolha != st.session_state["current_step"]:
            goto_step(escolha)
            st.rerun()


def render_step_footer():
    idx = STEPS.index(st.session_state["current_step"])
    c1, c2, c3 = st.columns([1, 1, 4])

    with c1:
        if idx > 0 and st.button("⬅ Etapa anterior", key=f"footer_prev_{idx}"):
            prev_step()
            st.rerun()

    with c2:
        if idx < len(STEPS) - 1 and st.button("Próxima etapa ➜", key=f"footer_next_{idx}"):
            next_step()
            st.rerun()


st.title("🧠 EduAI Studio - v7.5.1")
st.caption("Navegação simplificada por etapas e prompts alimentados por uma base única do aluno.")

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

    c1.text_input("Nome", key="nome")
    c2.text_input("Apelido", key="apelido")
    c1.text_input("Idade", key="idade")
    c2.text_input("Série / Ano", key="serie")
    c1.text_input("Escola", key="escola")
    c2.text_input("Turno", key="turno")
    st.text_input("Nome do responsável", key="responsavel")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Salvar ou carregar perfil do aluno")
    c1, c2 = st.columns([2, 1])

    c1.text_input(
        "Nome para salvar este perfil",
        key="novo_nome_perfil",
        placeholder="Ex: Filho 1, Gustavo, Aluna Ana"
    )

    if c2.button("Salvar aluno", key="salvar_aluno_btn"):
        nome_salvar = st.session_state["novo_nome_perfil"].strip()
        if nome_salvar:
            save_named_profile(nome_salvar)
            set_nav_message(f"Perfil '{nome_salvar}' salvo com sucesso.", "success")
            st.rerun()
        else:
            set_nav_message("Digite um nome para salvar o perfil.", "warning")
            st.rerun()

    perfis_salvos = list(st.session_state["saved_profiles"].keys())
    if perfis_salvos:
        perfil_escolhido = st.selectbox(
            "Perfis salvos",
            [""] + perfis_salvos,
            key="perfil_salvo_select"
        )
        if st.button("Carregar perfil salvo", key="carregar_perfil_btn"):
            if perfil_escolhido:
                load_named_profile(perfil_escolhido)
                sync_all_checkbox_groups()
                atualizar_caracteristicas_sugeridas()
                set_nav_message(f"Perfil '{perfil_escolhido}' carregado.", "success")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Interesses")
    checkbox_group("Selecione os interesses da criança", INTERESSES_OPTIONS, "interesses", columns=4)
    if "Outro" in st.session_state["interesses"]:
        st.text_input("Outro interesse", key="interesses_outro")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Diagnósticos e características")
    checkbox_group("Selecione um ou mais diagnósticos", DIAG_OPTIONS, "diagnosticos", columns=3)

    if "Outro" in st.session_state["diagnosticos"]:
        st.text_input("Qual outro diagnóstico?", key="outro_diagnostico")

    atualizar_caracteristicas_sugeridas()

    st.text_area(
        "Características sugeridas automaticamente pelos diagnósticos",
        value=st.session_state.get("caracteristicas_sugeridas", ""),
        height=120,
        disabled=True
    )

    st.text_area(
        "Outras características (editável)",
        key="outras_caracteristicas",
        height=120
    )

    st.markdown('<div class="small">As características sugeridas e as adicionais são usadas para adaptar os prompts.</div>', unsafe_allow_html=True)
    render_step_footer()
    st.markdown('</div>', unsafe_allow_html=True)

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
        st.text_input("Descreva o tipo de erro mais comum", key="tipo_erro_outro")

    st.markdown("<hr>", unsafe_allow_html=True)

    checkbox_group("O que mais engaja", ENGAJAMENTO_OPTIONS, "engajamento", columns=3)
    if "Outro" in st.session_state["engajamento"]:
        st.text_input("Outro fator de engajamento", key="engajamento_outro")

    checkbox_group("Principal dificuldade", DIFICULDADE_OPTIONS, "principal_dificuldade", columns=3)
    if "Outro" in st.session_state["principal_dificuldade"]:
        st.text_input("Outra dificuldade observada", key="dificuldade_outro")

    checkbox_group("Sinais quando trava", TRAVA_OPTIONS, "sinais_quando_trava", columns=3)
    if "Outro" in st.session_state["sinais_quando_trava"]:
        st.text_input("Outro sinal quando trava", key="trava_outro")

    checkbox_group("Melhor forma de retomar", RETOMADA_OPTIONS, "melhor_forma_retomar", columns=3)
    if "Outro" in st.session_state["melhor_forma_retomar"]:
        st.text_input("Outra forma de retomar", key="retomada_outro")

    render_step_footer()
    st.markdown('</div>', unsafe_allow_html=True)

elif step == "Cronograma":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Plano de estudo até a prova")

    st.text_input("Matéria", key="cron_materia")
    st.selectbox("Área da matéria (opcional)", AREA_MATERIA_OPTIONS, key="cron_area_materia")

    hoje = st.date_input("Data de hoje", value=datetime.date.today(), key="cron_hoje_input")
    prova = st.date_input("Data da prova", value=datetime.date.today(), key="cron_prova_input")

    st.caption(f"Data de hoje: {formatar_data_br(hoje)}")
    st.caption(f"Data da prova: {formatar_data_br(prova)}")

    perfil_para_cronograma = get_profile_base(prova)

    st.markdown("**Base do aluno usada no cronograma**")
    st.text_area(
        "Resumo do perfil usado",
        value=str(perfil_para_cronograma),
        height=220
    )

    st.text_area("Conteúdos da prova", key="cron_conteudos", height=120)

    a1, a2, a3 = st.columns(3)
    a1.text_area("Prioridade alta", key="cron_alta", height=110)
    a2.text_area("Prioridade média", key="cron_media", height=110)
    a3.text_area("Prioridade baixa", key="cron_baixa", height=110)

    txt_cron = prompt_cronograma(
        perfil_para_cronograma,
        st.session_state["cron_materia"],
        st.session_state["cron_area_materia"],
        st.session_state["cron_conteudos"],
        formatar_data_br(hoje),
        formatar_data_br(prova),
        st.session_state["cron_alta"],
        st.session_state["cron_media"],
        st.session_state["cron_baixa"]
    )

    st.text_area("Prompt de cronograma", value=txt_cron, height=380)

    st.markdown("**Usar a saída do cronograma na etapa Configuração**")
    st.text_area("Cole aqui a linha do dia gerada no cronograma", key="cronograma_linha_do_dia", height=90)

    if st.button("Usar essa linha na Configuração", key="cron_usar_linha_btn"):
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

        set_nav_message("Matéria, conteúdo do dia e objetivo foram enviados para Configuração.", "success")
        st.rerun()

    render_step_footer()
    st.markdown('</div>', unsafe_allow_html=True)

elif step == "Configuração":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Configuração didática do dia")

    st.text_input("Matéria", key="mat_did")
    st.selectbox("Área da matéria (opcional)", AREA_MATERIA_OPTIONS, key="config_area_materia")
    st.text_area("Conteúdo do dia", key="conteudo_dia", height=120)
    st.text_input("Objetivo do dia (opcional)", key="objetivo_dia")

    hoje2 = st.date_input("Data de hoje", value=datetime.date.today(), key="config_did_hoje")
    prova2 = st.date_input("Data da prova", value=datetime.date.today(), key="config_did_prova")

    st.caption(f"Data de hoje: {formatar_data_br(hoje2)}")
    st.caption(f"Data da prova: {formatar_data_br(prova2)}")

    radio_group("Situação do conteúdo", SITUACAO_OPTIONS, "situacao_conteudo", horizontal=True)
    radio_group("Prioridade do conteúdo", PRIORIDADE_OPTIONS, "prioridade_conteudo", horizontal=True)

    st.toggle("Usar com fontes anexadas no NotebookLM", key="usa_fontes")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Como a escola cobra")
    checkbox_group("Selecione os formatos mais comuns", ESCOLA_COBRANCA_OPTIONS, "cobranca_escola", columns=3)
    if "Outro" in st.session_state["cobranca_escola"]:
        st.text_input("Outro tipo de cobrança", key="cobranca_extra")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Materiais")
    checkbox_group(
        "Escolha os materiais",
        ["Vídeo", "Áudio (responsável)", "Slides", "Flashcards (máx 10)", "Teste"],
        "selected_materials",
        columns=3
    )
    st.info(
        f"Dias até a prova: {(prova2 - hoje2).days} | "
        f"Modo sugerido: {('revisão estratégica' if (prova2 - hoje2).days <= 1 else 'consolidação')}"
    )
    render_step_footer()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Resumo do perfil atual")
    perfil_config = get_profile_base(prova2)
    st.text_area("Resumo estruturado", value=str(perfil_config), height=260)
    st.markdown('</div>', unsafe_allow_html=True)

elif step == "Studio":
    try:
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
    situacao = st.session_state["situacao_conteudo"]
    prioridade = st.session_state["prioridade_conteudo"]

    st.subheader("Studio")
    st.caption("Prompts curtos para colar no NotebookLM Studio e gerar o material final.")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Base usada nos prompts")
    base_prompt_studio = contexto_studio_compacto(
        perfil, materia, area, conteudo, estilo, situacao, prioridade, days, usa
    )
    st.text_area("Base real enviada para os prompts", value=base_prompt_studio, height=360)
    st.markdown('</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Vídeo")
        st.text_area(
            "Prompt de vídeo",
            value=prompt_video(perfil, materia, area, conteudo, estilo, situacao, prioridade, days, usa),
            height=230
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Slides")
        st.text_area(
            "Prompt de slides",
            value=prompt_slides(perfil, materia, area, conteudo, estilo, situacao, prioridade, days, usa),
            height=230
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Flashcards")
        st.text_area(
            "Prompt de flashcards",
            value=prompt_flash(perfil, materia, area, conteudo, estilo, situacao, prioridade, days, usa),
            height=230
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Áudio do responsável")
        st.text_area(
            "Prompt de áudio",
            value=prompt_audio(perfil, materia, area, conteudo, estilo, situacao, prioridade, days, usa),
            height=250
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Teste")
        st.text_area(
            "Prompt de teste",
            value=prompt_teste(perfil, materia, area, conteudo, estilo, situacao, prioridade, days, usa),
            height=230
        )
        st.markdown('</div>', unsafe_allow_html=True)

    render_step_footer()

elif step == "Aula Completa":
    try:
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
        estilo,
        st.session_state["situacao_conteudo"],
        st.session_state["prioridade_conteudo"],
        days,
        st.session_state["selected_materials"],
        st.session_state["usa_fontes"]
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Pacote de aula completa")
    st.text_area("Aula completa", value=aula, height=420)
    render_step_footer()
    st.markdown('</div>', unsafe_allow_html=True)