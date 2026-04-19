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
from state import init_state
from ui_components import inject_styles, checkbox_group, radio_group, slugify
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
from storage import load_profiles, save_profile, delete_profile

st.set_page_config(page_title="EduAI Studio", page_icon="🧠", layout="wide")
init_state()
inject_styles()

# estado base
st.session_state.setdefault("saved_profiles", load_profiles())
st.session_state.setdefault("current_step", "Perfil")
st.session_state.setdefault("nav_message", "")
st.session_state.setdefault("nav_message_type", "info")
st.session_state.setdefault("novo_nome_perfil", "")
st.session_state.setdefault("perfil_sidebar_select", "")

# utilidades
def set_nav_message(msg, tp="info"):
    st.session_state["nav_message"] = msg
    st.session_state["nav_message_type"] = tp

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

def footer_nav():
    c1, c2, _ = st.columns([1, 1, 4])
    with c1:
        if STEPS.index(st.session_state["current_step"]) > 0:
            if st.button("⬅ Anterior", use_container_width=True, key=f"prev_{st.session_state['current_step']}"):
                prev_step()
    with c2:
        if STEPS.index(st.session_state["current_step"]) < len(STEPS) - 1:
            if st.button("Próxima ➜", use_container_width=True, key=f"next_{st.session_state['current_step']}"):
                next_step()

def sync_checkbox_group_keys(state_key, options):
    selected = set(st.session_state.get(state_key, []))
    for option in options:
        widget_key = f"{state_key}_{slugify(option)}"
        st.session_state[widget_key] = bool(option in selected)

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

def get_profile():
    atualizar_caracteristicas_sugeridas()
    return get_perfil_data()

def get_profile_payload():
    atualizar_caracteristicas_sugeridas()
    return {
        "nome": st.session_state.get("nome", ""),
        "apelido": st.session_state.get("apelido", ""),
        "idade": st.session_state.get("idade", ""),
        "serie": st.session_state.get("serie", ""),
        "escola": st.session_state.get("escola", ""),
        "turno": st.session_state.get("turno", ""),
        "responsavel": st.session_state.get("responsavel", ""),
        "interesses": st.session_state.get("interesses", []),
        "interesses_outro": st.session_state.get("interesses_outro", ""),
        "diagnosticos": st.session_state.get("diagnosticos", []),
        "outro_diagnostico": st.session_state.get("outro_diagnostico", ""),
        "caracteristicas_sugeridas": st.session_state.get("caracteristicas_sugeridas", ""),
        "outras_caracteristicas": st.session_state.get("outras_caracteristicas", ""),
        "atencao_sustentada": st.session_state.get("atencao_sustentada", "Média"),
        "autonomia": st.session_state.get("autonomia", "Alguma mediação"),
        "canal_preferencial": st.session_state.get("canal_preferencial", "Visual"),
        "tolerancia_frustracao": st.session_state.get("tolerancia_frustracao", "Média"),
        "leitura_nivel": st.session_state.get("leitura_nivel", "Adequado"),
        "escrita_nivel": st.session_state.get("escrita_nivel", "Adequado"),
        "matematica_nivel": st.session_state.get("matematica_nivel", "Adequado"),
        "compreensao_oral": st.session_state.get("compreensao_oral", "Média"),
        "tipo_erro_mais_comum": st.session_state.get("tipo_erro_mais_comum", []),
        "tipo_erro_outro": st.session_state.get("tipo_erro_outro", ""),
        "engajamento": st.session_state.get("engajamento", []),
        "engajamento_outro": st.session_state.get("engajamento_outro", ""),
        "principal_dificuldade": st.session_state.get("principal_dificuldade", []),
        "dificuldade_outro": st.session_state.get("dificuldade_outro", ""),
        "sinais_quando_trava": st.session_state.get("sinais_quando_trava", []),
        "trava_outro": st.session_state.get("trava_outro", ""),
        "melhor_forma_retomar": st.session_state.get("melhor_forma_retomar", []),
        "retomada_outro": st.session_state.get("retomada_outro", ""),
    }

def apply_profile_payload(payload):
    for k, v in payload.items():
        st.session_state[k] = v
    sync_all_checkbox_groups()
    atualizar_caracteristicas_sugeridas()

def show_prompt_block(title, text, key_name):
    st.markdown(f"#### {title}")
    st.code(text, language="text")
    with st.expander("Visualizar em caixa de texto"):
        st.text_area(f"{title} (visualização)", value=text, height=220, key=f"txt_{key_name}")

def apply_cronograma_to_config():
    campos = extrair_campos_cronograma(st.session_state.get("cronograma_linha_do_dia", ""))

    if st.session_state.get("cron_materia", "").strip():
        st.session_state["mat_did"] = st.session_state["cron_materia"].strip()

    st.session_state["config_area_materia"] = st.session_state.get("cron_area_materia", "")
    st.session_state["config_did_hoje"] = st.session_state.get("cron_hoje_input", datetime.date.today())
    st.session_state["config_did_prova"] = st.session_state.get("cron_prova_input", datetime.date.today())
    st.session_state["conteudo_dia"] = (
        campos["texto_colar"]
        or campos["conteudo"]
        or st.session_state.get("cronograma_linha_do_dia", "").strip()
    )

    if campos["objetivo"]:
        st.session_state["objetivo_dia"] = campos["objetivo"]

    set_nav_message("Linha enviada para Configuração.", "success")

# sincroniza checkboxes com valores salvos
sync_all_checkbox_groups()

# sidebar
with st.sidebar:
    st.markdown("## Etapas")
    current_idx = STEPS.index(st.session_state["current_step"])
    st.progress((current_idx + 1) / len(STEPS))
    st.caption(f"Etapa {current_idx + 1} de {len(STEPS)}")

    for step in STEPS:
        emoji = "👉 " if step == st.session_state["current_step"] else ""
        if st.button(f"{emoji}{step}", use_container_width=True, key=f"nav_{step}"):
            goto_step(step)

    st.markdown("---")
    st.markdown("## Perfis salvos")

    perfis = load_profiles()
    st.session_state["saved_profiles"] = perfis
    nomes = sorted(list(perfis.keys()))

    if nomes:
        perfil_sel = st.selectbox("Selecionar perfil", [""] + nomes, key="perfil_sidebar_select")
        c1, c2 = st.columns(2)

        with c1:
            if st.button("Carregar", use_container_width=True, key="load_profile_sidebar"):
                if perfil_sel:
                    apply_profile_payload(perfis[perfil_sel])
                    set_nav_message(f"Perfil '{perfil_sel}' carregado.", "success")
                    st.rerun()

        with c2:
            if st.button("Excluir", use_container_width=True, key="delete_profile_sidebar"):
                if perfil_sel:
                    delete_profile(perfil_sel)
                    st.session_state["saved_profiles"] = load_profiles()
                    st.session_state["perfil_sidebar_select"] = ""
                    set_nav_message(f"Perfil '{perfil_sel}' excluído.", "success")
                    st.rerun()
    else:
        st.caption("Nenhum perfil salvo.")

# header
st.title("🧠 EduAI Studio")
st.caption("Fluxo estável, prompts curtos e perfis persistentes.")

if st.session_state["nav_message"]:
    tp = st.session_state["nav_message_type"]
    if tp == "success":
        st.success(st.session_state["nav_message"])
    elif tp == "warning":
        st.warning(st.session_state["nav_message"])
    else:
        st.info(st.session_state["nav_message"])

step = st.session_state["current_step"]

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
    checkbox_group("Interesses", INTERESSES_OPTIONS, "interesses", columns=4)
    if "Outro" in st.session_state.get("interesses", []):
        st.text_input("Outro interesse", key="interesses_outro")

    st.markdown("### Diagnósticos")
    checkbox_group("Diagnósticos", DIAG_OPTIONS, "diagnosticos", columns=3)
    if "Outro" in st.session_state.get("diagnosticos", []):
        st.text_input("Outro diagnóstico", key="outro_diagnostico")

    atualizar_caracteristicas_sugeridas()

    st.text_area(
        "Características sugeridas automaticamente",
        value=st.session_state.get("caracteristicas_sugeridas", ""),
        height=140,
        disabled=True
    )

    st.text_area("Outras características", key="outras_caracteristicas", height=120)

    st.markdown("### Salvar perfil")
    c1, c2 = st.columns([3, 1])
    with c1:
        st.text_input("Nome para salvar", key="novo_nome_perfil")
    with c2:
        if st.button("Salvar", key="save_profile_btn"):
            nome = st.session_state.get("novo_nome_perfil", "").strip()
            if nome:
                save_profile(nome, get_profile_payload())
                st.session_state["saved_profiles"] = load_profiles()
                set_nav_message("Perfil salvo.", "success")
                st.rerun()

    footer_nav()

elif step == "Aprendizagem":
    st.subheader("Perfil de aprendizagem")

    radio_group("Atenção sustentada", ATENCAO_OPTIONS, "atencao_sustentada", horizontal=True)
    radio_group("Autonomia", AUTONOMIA_OPTIONS, "autonomia", horizontal=True)
    radio_group("Canal preferencial", CANAL_OPTIONS, "canal_preferencial", horizontal=True)
    radio_group("Tolerância à frustração", FRUSTRACAO_OPTIONS, "tolerancia_frustracao", horizontal=True)

    radio_group("Leitura", NIVEL_OPTIONS, "leitura_nivel", horizontal=True)
    radio_group("Escrita", NIVEL_OPTIONS, "escrita_nivel", horizontal=True)
    radio_group("Matemática", NIVEL_OPTIONS, "matematica_nivel", horizontal=True)
    radio_group("Compreensão oral", ["Baixa", "Média", "Boa"], "compreensao_oral", horizontal=True)

    st.markdown("---")

    checkbox_group("Tipo de erro mais comum", ERRO_OPTIONS, "tipo_erro_mais_comum", columns=3)
    if "Outro" in st.session_state.get("tipo_erro_mais_comum", []):
        st.text_input("Outro tipo de erro", key="tipo_erro_outro")

    checkbox_group("O que mais engaja", ENGAJAMENTO_OPTIONS, "engajamento", columns=3)
    if "Outro" in st.session_state.get("engajamento", []):
        st.text_input("Outro engajamento", key="engajamento_outro")

    checkbox_group("Principal dificuldade", DIFICULDADE_OPTIONS, "principal_dificuldade", columns=3)
    if "Outro" in st.session_state.get("principal_dificuldade", []):
        st.text_input("Outra dificuldade", key="dificuldade_outro")

    checkbox_group("Sinais quando trava", TRAVA_OPTIONS, "sinais_quando_trava", columns=3)
    if "Outro" in st.session_state.get("sinais_quando_trava", []):
        st.text_input("Outro sinal", key="trava_outro")

    checkbox_group("Melhor forma de retomar", RETOMADA_OPTIONS, "melhor_forma_retomar", columns=3)
    if "Outro" in st.session_state.get("melhor_forma_retomar", []):
        st.text_input("Outra forma de retomar", key="retomada_outro")

    footer_nav()

elif step == "Cronograma":
    st.subheader("Cronograma até a prova")

    st.text_input("Matéria", key="cron_materia")
    st.selectbox("Área", AREA_MATERIA_OPTIONS, key="cron_area_materia")

    hoje = st.date_input("Hoje", key="cron_hoje_input", value=st.session_state.get("cron_hoje_input", datetime.date.today()))
    prova = st.date_input("Data da prova", key="cron_prova_input", value=st.session_state.get("cron_prova_input", datetime.date.today()))

    st.caption(f"Hoje: {formatar_data_br(hoje)}")
    st.caption(f"Prova: {formatar_data_br(prova)}")

    st.text_area("Conteúdos", key="cron_conteudos", height=120)

    txt = prompt_cronograma(
        get_profile(),
        st.session_state.get("cron_materia", ""),
        st.session_state.get("cron_area_materia", ""),
        st.session_state.get("cron_conteudos", ""),
        formatar_data_br(hoje),
        formatar_data_br(prova),
        st.session_state.get("cron_alta", ""),
        st.session_state.get("cron_media", ""),
        st.session_state.get("cron_baixa", ""),
    )

    show_prompt_block("Prompt do cronograma", txt, "cron")

    st.text_area("Linha do dia", key="cronograma_linha_do_dia", height=90)

    if st.button("Usar esta linha na Configuração"):
        apply_cronograma_to_config()
        goto_step("Configuração")

    footer_nav()

elif step == "Configuração":
    st.subheader("Configuração do estudo")

    st.text_input("Matéria", key="mat_did")
    st.selectbox("Área", AREA_MATERIA_OPTIONS, key="config_area_materia")

    st.text_area("Conteúdo do dia", key="conteudo_dia", height=120)
    st.text_input("Objetivo", key="objetivo_dia")

    hoje2 = st.date_input("Hoje", key="config_did_hoje", value=st.session_state.get("config_did_hoje", datetime.date.today()))
    prova2 = st.date_input("Data da prova", key="config_did_prova", value=st.session_state.get("config_did_prova", datetime.date.today()))

    radio_group("Situação do conteúdo", SITUACAO_OPTIONS, "situacao_conteudo", horizontal=True)
    radio_group("Prioridade", PRIORIDADE_OPTIONS, "prioridade_conteudo", horizontal=True)

    checkbox_group("Como a escola cobra", ESCOLA_COBRANCA_OPTIONS, "cobranca_escola", columns=3)
    if "Outro" in st.session_state.get("cobranca_escola", []):
        st.text_input("Outro tipo de cobrança", key="cobranca_extra")

    checkbox_group(
        "Materiais",
        ["Vídeo", "Áudio (responsável)", "Slides", "Flashcards (máx 10)", "Teste"],
        "selected_materials",
        columns=3
    )

    footer_nav()

elif step == "Studio":
    prova = st.session_state.get("config_did_prova", datetime.date.today())
    hoje = st.session_state.get("config_did_hoje", datetime.date.today())
    dias = (prova - hoje).days

    perfil = get_profile()
    estilo = obter_cobranca()

    materia = st.session_state.get("mat_did", "")
    area = st.session_state.get("config_area_materia", "")
    conteudo = st.session_state.get("conteudo_dia", "")
    objetivo = st.session_state.get("objetivo_dia", "")
    situacao = st.session_state.get("situacao_conteudo", "novo")
    prioridade = st.session_state.get("prioridade_conteudo", "alta")
    usa_fontes = False

    materiais = st.session_state.get("selected_materials", [])

    if "Vídeo" in materiais:
        show_prompt_block(
            "Prompt Vídeo",
            prompt_video(perfil, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_compacto),
            "video"
        )

    if "Áudio (responsável)" in materiais:
        show_prompt_block(
            "Prompt Áudio",
            prompt_audio(perfil, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_compacto),
            "audio"
        )

    if "Slides" in materiais:
        show_prompt_block(
            "Prompt Slides",
            prompt_slides(perfil, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_compacto),
            "slides"
        )

    if "Flashcards (máx 10)" in materiais:
        show_prompt_block(
            "Prompt Flashcards",
            prompt_flash(perfil, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_compacto),
            "flash"
        )

    if "Teste" in materiais:
        show_prompt_block(
            "Prompt Teste",
            prompt_teste(perfil, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_compacto),
            "teste"
        )

    footer_nav()

elif step == "Aula Completa":
    prova = st.session_state.get("config_did_prova", datetime.date.today())
    hoje = st.session_state.get("config_did_hoje", datetime.date.today())
    dias = (prova - hoje).days

    txt = prompt_aula(
        get_profile(),
        st.session_state.get("mat_did", ""),
        st.session_state.get("config_area_materia", ""),
        st.session_state.get("conteudo_dia", ""),
        st.session_state.get("objetivo_dia", ""),
        obter_cobranca(),
        st.session_state.get("situacao_conteudo", "novo"),
        st.session_state.get("prioridade_conteudo", "alta"),
        dias,
        st.session_state.get("selected_materials", []),
        False,
        modo_estudo
    )

    show_prompt_block("Pacote completo", txt, "aula")
    footer_nav()
