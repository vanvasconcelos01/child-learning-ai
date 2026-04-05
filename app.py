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
from ui_components import inject_styles, checkbox_group, radio_group
from profile_logic import (
    formatar_data_br,
    atualizar_caracteristicas_sugeridas,
    get_perfil_data,
    exportar_perfil_json,
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

def goto_step(step_name: str):
    st.session_state["current_step"] = step_name
    st.rerun()

def render_step_navigation():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Etapas")
    st.segmented_control(
        "Fluxo do app",
        options=STEPS,
        key="current_step",
        selection_mode="single",
    )

    idx = STEPS.index(st.session_state["current_step"])
    c1, c2, c3 = st.columns([1, 1, 3])

    with c1:
        if idx > 0 and st.button("⬅ Anterior", key=f"prev_{idx}"):
            goto_step(STEPS[idx - 1])

    with c2:
        if idx < len(STEPS) - 1 and st.button("Próxima ➜", key=f"next_{idx}"):
            goto_step(STEPS[idx + 1])

    st.markdown('</div>', unsafe_allow_html=True)

st.title("🧠 EduAI Studio - v7.3")
st.caption("Navegação real por etapas, área opcional da matéria e especialização pedagógica ampliada.")

render_step_navigation()

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

    c1.text_input("Nome para salvar este perfil", key="novo_nome_perfil", placeholder="Ex: Filho 1, Gustavo, Aluna Ana")
    if c2.button("Salvar aluno", key="salvar_aluno_btn"):
        nome_salvar = st.session_state["novo_nome_perfil"].strip()
        if nome_salvar:
            save_named_profile(nome_salvar)
            st.success(f"Perfil '{nome_salvar}' salvo com sucesso.")
        else:
            st.warning("Digite um nome para salvar o perfil.")

    perfis_salvos = list(st.session_state["saved_profiles"].keys())
    if perfis_salvos:
        perfil_escolhido = st.selectbox("Perfis salvos", [""] + perfis_salvos, key="perfil_salvo_select")
        if st.button("Carregar perfil salvo", key="carregar_perfil_btn"):
            if perfil_escolhido:
                load_named_profile(perfil_escolhido)
                st.success(f"Perfil '{perfil_escolhido}' carregado.")
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

    if st.button("Ir para Aprendizagem", key="goto_aprendizagem_btn"):
        goto_step("Aprendizagem")

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

    if st.button("Ir para Cronograma", key="goto_cronograma_btn"):
        goto_step("Cronograma")

    st.markdown('</div>', unsafe_allow_html=True)

elif step == "Cronograma":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Plano de estudo até a prova")

    st.text_input("Matéria", key="cron_materia")
    st.selectbox("Área da matéria (opcional)", AREA_MATERIA_OPTIONS, key="area_materia")

    hoje = st.date_input("Data de hoje", value=datetime.date.today(), key="cron_hoje_input")
    prova = st.date_input("Data da prova", value=datetime.date.today(), key="cron_prova_input")

    st.caption(f"Data de hoje: {formatar_data_br(hoje)}")
    st.caption(f"Data da prova: {formatar_data_br(prova)}")

    st.markdown("**Prévia do perfil que será usado no cronograma**")
    st.write({
        "nome": st.session_state.get("nome", ""),
        "apelido": st.session_state.get("apelido", ""),
        "idade": st.session_state.get("idade", ""),
        "serie": st.session_state.get("serie", ""),
        "escola": st.session_state.get("escola", ""),
        "turno": st.session_state.get("turno", ""),
        "responsavel": st.session_state.get("responsavel", "")
    })

    st.text_area("Conteúdos da prova", key="cron_conteudos", height=120)

    a1, a2, a3 = st.columns(3)
    a1.text_area("Prioridade alta", key="cron_alta", height=110)
    a2.text_area("Prioridade média", key="cron_media", height=110)
    a3.text_area("Prioridade baixa", key="cron_baixa", height=110)

    txt_cron = prompt_cronograma(
        get_perfil_data(formatar_data_br(prova)),
        st.session_state["cron_materia"],
        st.session_state["area_materia"],
        st.session_state["cron_conteudos"],
        formatar_data_br(hoje),
        formatar_data_br(prova),
        st.session_state["cron_alta"],
        st.session_state["cron_media"],
        st.session_state["cron_baixa"]
    )

    st.text_area("Prompt de cronograma", value=txt_cron, height=360)

    st.markdown("**Usar a saída do cronograma na etapa Configuração**")
    st.text_area("Cole aqui a linha do dia gerada no cronograma", key="cronograma_linha_do_dia", height=90)

    if st.button("Usar essa linha na Configuração", key="cron_usar_linha_btn"):
        campos = extrair_campos_cronograma(st.session_state["cronograma_linha_do_dia"])

        if st.session_state["cron_materia"].strip():
            st.session_state["mat_did"] = st.session_state["cron_materia"].strip()

        st.session_state["conteudo_dia"] = (
            campos["texto_colar"]
            or campos["conteudo"]
            or st.session_state["cronograma_linha_do_dia"].strip()
        )

        if campos["objetivo"]:
            st.session_state["objetivo_dia"] = campos["objetivo"]

        st.success("Matéria, conteúdo do dia e objetivo foram enviados para Configuração.")

    if st.button("Ir para Configuração", key="goto_config_btn"):
        goto_step("Configuração")

    st.markdown('</div>', unsafe_allow_html=True)

elif step == "Configuração":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Configuração didática do dia")

    st.text_input("Matéria", key="mat_did")
    st.selectbox("Área da matéria (opcional)", AREA_MATERIA_OPTIONS, key="area_materia")
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

    if st.button("Ir para Studio", key="goto_studio_btn"):
        goto_step("Studio")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Resumo do perfil atual")
    st.text_area("Resumo estruturado", value=exportar_perfil_json(), height=260)
    st.markdown('</div>', unsafe_allow_html=True)

elif step == "Studio":
    try:
        days = (prova2 - hoje2).days
        estilo = obter_cobranca()
    except Exception:
        days = 0
        estilo = ""
        prova2 = datetime.date.today()

    perfil = get_perfil_data(formatar_data_br(prova2))
    usa = st.session_state["usa_fontes"]
    materia = st.session_state["mat_did"]
    area = st.session_state["area_materia"]
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
        st.text_area("Prompt de vídeo", value=prompt_video(perfil, materia, area, conteudo, estilo, situacao, prioridade, days, usa), height=230)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Slides")
        st.text_area("Prompt de slides", value=prompt_slides(perfil, materia, area, conteudo, estilo, situacao, prioridade, days, usa), height=230)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Flashcards")
        st.text_area("Prompt de flashcards", value=prompt_flash(perfil, materia, area, conteudo, estilo, situacao, prioridade, days, usa), height=230)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Áudio do responsável")
        st.text_area("Prompt de áudio", value=prompt_audio(perfil, materia, area, conteudo, estilo, situacao, prioridade, days, usa), height=250)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Teste")
        st.text_area("Prompt de teste", value=prompt_teste(perfil, materia, area, conteudo, estilo, situacao, prioridade, days, usa), height=230)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Ir para Aula Completa", key="goto_aula_btn"):
        goto_step("Aula Completa")

elif step == "Aula Completa":
    try:
        days = (prova2 - hoje2).days
        estilo = obter_cobranca()
    except Exception:
        days = 0
        estilo = ""
        prova2 = datetime.date.today()

    perfil = get_perfil_data(formatar_data_br(prova2))
    aula = prompt_aula(
        perfil,
        st.session_state["mat_did"],
        st.session_state["area_materia"],
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
    st.markdown('</div>', unsafe_allow_html=True)
