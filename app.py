import streamlit as st
import datetime
import json
import re

st.set_page_config(page_title="EduAI Studio", page_icon="🧠", layout="wide")

# ======================
# CONSTANTES
# ======================

PT_MONTHS = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril", 5: "maio", 6: "junho",
    7: "julho", 8: "agosto", 9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}

DIAG_OPTIONS = [
    "TDAH", "TEA nível 1", "TEA nível 2", "TEA nível 3",
    "Dislexia", "Discalculia", "Processamento auditivo",
    "Ansiedade", "TOD", "Outro"
]

DIAG_CHARACTERISTICS = {
    "TDAH": [
        "atenção curta",
        "beneficia-se de blocos curtos",
        "precisa de ritmo dinâmico",
        "responde melhor a objetivos claros e rápidos",
        "aprende melhor com estímulos visuais e interação"
    ],
    "TEA nível 1": [
        "beneficia-se de previsibilidade",
        "precisa de instruções claras e objetivas",
        "pode ter dificuldade com linguagem ambígua",
        "responde bem a rotinas estruturadas"
    ],
    "TEA nível 2": [
        "necessita maior estrutura e mediação",
        "precisa de previsibilidade e linguagem muito clara",
        "beneficia-se de passo a passo explícito",
        "pode demandar apoio mais frequente para transições"
    ],
    "TEA nível 3": [
        "necessita alto suporte",
        "precisa de linguagem simples, direta e previsível",
        "beneficia-se de rotinas muito estruturadas",
        "demanda mediação intensiva e apoio constante"
    ],
    "Dislexia": [
        "beneficia-se de menor carga textual",
        "precisa de frases mais curtas",
        "responde melhor a apoio visual",
        "pode cansar com leitura longa"
    ],
    "Discalculia": [
        "precisa de apoio concreto e visual",
        "beneficia-se de progressão muito gradual",
        "responde melhor a exemplos práticos",
        "pode travar diante de abstrações numéricas rápidas"
    ],
    "Processamento auditivo": [
        "beneficia-se de apoio visual constante",
        "pode ter dificuldade com instruções longas faladas",
        "precisa de mensagens curtas e objetivas",
        "responde melhor quando vê e ouve ao mesmo tempo"
    ],
    "Ansiedade": [
        "pode travar sob pressão",
        "precisa de segurança e progressão leve",
        "beneficia-se de previsibilidade e encorajamento objetivo",
        "responde melhor quando o erro é tratado com calma"
    ],
    "TOD": [
        "pode reagir melhor a linguagem neutra e respeitosa",
        "beneficia-se de escolhas simples e combinados claros",
        "responde melhor a estrutura firme sem confronto"
    ],
}

INTERESSES_OPTIONS = [
    "games",
    "histórias de fantasia",
    "futebol",
    "Pokémon",
    "música",
    "desenhos",
    "arte",
    "animais",
    "dinossauros",
    "super-heróis",
    "Minecraft",
    "Roblox",
    "ciência",
    "espaço",
    "mistério",
    "aventura",
    "livros",
    "corridas",
    "dança",
    "tecnologia",
    "Outro"
]

ESCOLA_COBRANCA_OPTIONS = [
    "questões objetivas",
    "questões dissertativas curtas",
    "interpretação de texto",
    "interpretação com imagens",
    "situações do cotidiano",
    "resolução passo a passo",
    "comparação entre conceitos",
    "associação de colunas",
    "verdadeiro ou falso",
    "completar lacunas",
    "sequência lógica / ordenação",
    "mapas, gráficos ou tabelas",
    "vocabulário e definições",
    "produção de resposta oral",
    "Outro"
]

ATENCAO_OPTIONS = ["Muito baixa", "Baixa", "Média", "Boa"]
AUTONOMIA_OPTIONS = ["Precisa de muita mediação", "Precisa de alguma mediação", "Quase independente"]
CANAL_OPTIONS = ["Visual", "Auditivo", "Leitura guiada", "Manipulação / concreto", "Misto"]
FRUSTRACAO_OPTIONS = ["Baixa", "Média", "Boa"]
NIVEL_OPTIONS = ["Abaixo do esperado", "Adequado", "Acima do esperado"]
ERRO_OPTIONS = ["Trava", "Chuta", "Dispersa", "Fica ansioso", "Recusa", "Outro"]

ENGAJAMENTO_OPTIONS = [
    "desafios curtos",
    "competição leve",
    "exemplos visuais",
    "histórias e narrativa",
    "jogos e quizzes",
    "curiosidades",
    "atividades práticas",
    "recompensa rápida",
    "passo a passo guiado",
    "variação de estímulos",
    "Outro"
]

DIFICULDADE_OPTIONS = [
    "manter atenção até o fim",
    "entender enunciados longos",
    "organizar o pensamento",
    "memorizar conteúdo",
    "interpretar texto",
    "resolver sozinho",
    "começar a atividade",
    "lidar com erros",
    "fazer cálculos mentalmente",
    "acompanhar explicações orais longas",
    "Outro"
]

TRAVA_OPTIONS = [
    "fica disperso",
    "muda de assunto",
    "diz que não sabe",
    "chuta respostas",
    "fica ansioso",
    "se irrita",
    "fica em silêncio",
    "quer parar",
    "pede ajuda imediatamente",
    "demora para começar",
    "Outro"
]

RETOMADA_OPTIONS = [
    "dividir em partes menores",
    "dar exemplo parecido",
    "usar apoio visual",
    "ler junto",
    "fazer pergunta mais simples",
    "dar duas opções",
    "retomar do último acerto",
    "pausa curta e voltar",
    "reforço positivo objetivo",
    "transformar em desafio curto",
    "Outro"
]

SITUACAO_OPTIONS = ["novo", "ja_visto", "em_dificuldade"]
PRIORIDADE_OPTIONS = ["alta", "media", "baixa"]

# ======================
# DEFAULTS
# ======================

DEFAULTS = {
    "nome": "",
    "apelido": "",
    "idade": "",
    "serie": "",
    "escola": "",
    "turno": "",
    "interesses": [],
    "interesses_outro": "",
    "responsavel": "",

    "diagnosticos": [],
    "outro_diagnostico": "",
    "outras_caracteristicas": "",

    "usa_fontes": False,
    "selected_materials": ["Vídeo", "Áudio (responsável)", "Slides"],
    "cobranca_escola": [],
    "cobranca_extra": "",

    "atencao_sustentada": "Média",
    "autonomia": "Precisa de alguma mediação",
    "canal_preferencial": "Visual",
    "tolerancia_frustracao": "Média",
    "leitura_nivel": "Adequado",
    "escrita_nivel": "Adequado",
    "matematica_nivel": "Adequado",
    "compreensao_oral": "Média",
    "tipo_erro_mais_comum": "Trava",
    "tipo_erro_outro": "",

    "engajamento": [],
    "engajamento_outro": "",
    "principal_dificuldade": [],
    "dificuldade_outro": "",
    "sinais_quando_trava": [],
    "trava_outro": "",
    "melhor_forma_retomar": [],
    "retomada_outro": "",

    "cron_materia": "",
    "cron_conteudos": "",
    "cron_alta": "",
    "cron_media": "",
    "cron_baixa": "",
    "cronograma_linha_do_dia": "",

    "mat_did": "",
    "conteudo_dia": "",
    "objetivo_dia": "",
    "situacao_conteudo": "novo",
    "prioridade_conteudo": "alta",
}

for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)

# ======================
# HELPERS
# ======================

def formatar_data_br(d):
    return d.strftime("%d/%m/%Y")

def formatar_data_extenso(d):
    return f"{d.day} de {PT_MONTHS[d.month]} de {d.year}"

def modo_estudo(dias, situacao):
    if dias <= 1:
        return "revisão estratégica"
    if situacao == "novo":
        return "introdução guiada"
    if situacao == "em_dificuldade":
        return "reforço estruturado"
    return "consolidação"

def slugify(texto):
    return re.sub(r"[^a-zA-Z0-9]+", "_", texto.strip().lower())

def checkbox_group(label, options, state_key, columns=3):
    st.markdown(f"**{label}**")
    selected_set = set(st.session_state.get(state_key, []))
    cols = st.columns(columns)
    novos_selecionados = []

    for i, option in enumerate(options):
        widget_key = f"{state_key}_{slugify(option)}"
        default_value = option in selected_set

        if widget_key not in st.session_state or not isinstance(st.session_state.get(widget_key), bool):
            st.session_state[widget_key] = default_value

        with cols[i % columns]:
            marcado = st.checkbox(option, key=widget_key)

        if marcado:
            novos_selecionados.append(option)

    st.session_state[state_key] = novos_selecionados

def radio_group(label, options, state_key, horizontal=False):
    valor_atual = st.session_state.get(state_key, options[0])
    if valor_atual not in options:
        valor_atual = options[0]
    st.session_state[state_key] = st.radio(
        label,
        options,
        index=options.index(valor_atual),
        horizontal=horizontal,
        key=f"{state_key}_radio"
    )

def combine_characteristics(diags, outro=""):
    items, seen = [], set()
    for diag in diags:
        if diag == "Outro":
            continue
        for c in DIAG_CHARACTERISTICS.get(diag, []):
            if c not in seen:
                seen.add(c)
                items.append(c)
    if outro.strip() and outro.strip() not in seen:
        items.append(outro.strip())
    return ", ".join(items)

def juntar_multiselect_com_outro(lista_base, texto_outro):
    itens = list(lista_base) if lista_base else []
    usar_outro = "Outro" in itens
    itens = [x for x in itens if x != "Outro"]

    if usar_outro and texto_outro and texto_outro.strip():
        itens.append(texto_outro.strip())

    return ", ".join(itens) if itens else "não informado"

def obter_cobranca():
    return juntar_multiselect_com_outro(
        st.session_state["cobranca_escola"],
        st.session_state["cobranca_extra"]
    )

def obter_interesses():
    return juntar_multiselect_com_outro(
        st.session_state["interesses"],
        st.session_state["interesses_outro"]
    )

def obter_tipo_erro():
    erro = st.session_state["tipo_erro_mais_comum"]
    if erro == "Outro" and st.session_state["tipo_erro_outro"].strip():
        return st.session_state["tipo_erro_outro"].strip()
    return erro

def perfil_aprendizagem_texto():
    engajamento = juntar_multiselect_com_outro(
        st.session_state["engajamento"],
        st.session_state["engajamento_outro"]
    )
    dificuldade = juntar_multiselect_com_outro(
        st.session_state["principal_dificuldade"],
        st.session_state["dificuldade_outro"]
    )
    trava = juntar_multiselect_com_outro(
        st.session_state["sinais_quando_trava"],
        st.session_state["trava_outro"]
    )
    retomada = juntar_multiselect_com_outro(
        st.session_state["melhor_forma_retomar"],
        st.session_state["retomada_outro"]
    )

    return f"""
- Atenção sustentada: {st.session_state['atencao_sustentada']}
- Autonomia: {st.session_state['autonomia']}
- Canal preferencial: {st.session_state['canal_preferencial']}
- Tolerância à frustração: {st.session_state['tolerancia_frustracao']}
- Leitura: {st.session_state['leitura_nivel']}
- Escrita: {st.session_state['escrita_nivel']}
- Matemática: {st.session_state['matematica_nivel']}
- Compreensão oral: {st.session_state['compreensao_oral']}
- O que mais engaja: {engajamento}
- Principal dificuldade observada: {dificuldade}
- Tipo de erro mais comum: {obter_tipo_erro()}
- Sinais quando trava: {trava}
- Melhor forma de retomar: {retomada}
""".strip()

def get_perfil_data(data_prova=""):
    diagnosticos = list(st.session_state["diagnosticos"])
    if st.session_state["outro_diagnostico"].strip():
        diagnosticos.append(st.session_state["outro_diagnostico"].strip())

    return {
        "nome": st.session_state["nome"],
        "apelido": st.session_state["apelido"],
        "idade": st.session_state["idade"],
        "serie": st.session_state["serie"],
        "escola": st.session_state["escola"],
        "turno": st.session_state["turno"],
        "interesses": obter_interesses(),
        "responsavel": st.session_state["responsavel"],
        "diagnosticos": diagnosticos,
        "outras_caracteristicas": st.session_state["outras_caracteristicas"],
        "perfil_aprendizagem": perfil_aprendizagem_texto(),
        "data_prova": data_prova,
    }

def exportar_perfil_json():
    data = get_perfil_data()
    return json.dumps(data, ensure_ascii=False, indent=2)

def resumo_aluno_compacto(data):
    diags = ", ".join(data["diagnosticos"]) if data["diagnosticos"] else "nenhum"

    perfil_curto = (
        f"Atenção: {st.session_state['atencao_sustentada']}; "
        f"Autonomia: {st.session_state['autonomia']}; "
        f"Canal: {st.session_state['canal_preferencial']}; "
        f"Engaja com: {juntar_multiselect_com_outro(st.session_state['engajamento'], st.session_state['engajamento_outro'])}; "
        f"Dificuldade: {juntar_multiselect_com_outro(st.session_state['principal_dificuldade'], st.session_state['dificuldade_outro'])}; "
        f"Erro comum: {obter_tipo_erro()}; "
        f"Quando trava: {juntar_multiselect_com_outro(st.session_state['sinais_quando_trava'], st.session_state['trava_outro'])}; "
        f"Retomar: {juntar_multiselect_com_outro(st.session_state['melhor_forma_retomar'], st.session_state['retomada_outro'])}"
    )

    return (
        f"Aluno: {data['nome'] or 'não informado'}, "
        f"{data['idade'] or '?'} anos, {data['serie'] or 'série não informada'}. "
        f"Diagnósticos: {diags}. "
        f"Interesses: {data['interesses'] or 'não informado'}. "
        f"Perfil: {perfil_curto}."
    )

def build_base_prompt(data):
    diags = ", ".join(data["diagnosticos"]) if data["diagnosticos"] else "Nenhum"
    return f"""PROFESSOR PARTICULAR

Você é um professor particular especializado em adaptação pedagógica e personalização de materiais.

PERFIL DO ALUNO
Aluno: {data['nome']} ({data['apelido']})
Idade: {data['idade']}
Série: {data['serie']}
Escola: {data['escola']}
Turno: {data['turno']}
Responsável: {data['responsavel']}

DIAGNÓSTICOS
{diags}

PERFIL DE APRENDIZAGEM
{data['perfil_aprendizagem']}

OUTRAS CARACTERÍSTICAS
{data['outras_caracteristicas'] or 'não informado'}

INTERESSES
{data['interesses'] or 'não informado'}
"""

def contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    regras = (
        "- usar as fontes anexadas como base principal\n"
        "- não copiar literalmente\n"
        "- não inventar páginas"
        if usa_fontes else
        "- criar mesmo sem fontes anexadas\n"
        "- usar nível compatível com a série\n"
        "- não citar páginas"
    )
    return f"""{build_base_prompt(data)}
CONTEXTO
Matéria: {materia}
Conteúdo do dia: {conteudo}
Data da prova: {data['data_prova']}
Dias restantes: {dias}
Situação: {situacao}
Prioridade: {prioridade}
Modo de estudo: {modo_estudo(dias, situacao)}
Forma de cobrança: {estilo or 'não informada'}

IMPORTANTE
{regras}
- adaptar tudo ao perfil do aluno
- criar exemplos inéditos
- considerar o erro comum e a forma de retomada
"""

def contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    modo_fontes = "Usar as fontes anexadas como base." if usa_fontes else "Criar sem depender de fontes anexadas."

    return f"""Material personalizado.
Matéria: {materia}
Conteúdo: {conteudo}
Dias até a prova: {dias}
Situação: {situacao}
Prioridade: {prioridade}
Cobrança: {estilo or 'não informado'}
{modo_fontes}

Perfil:
{resumo_aluno_compacto(data)}

Regras:
- adaptar ao aluno
- considerar interesses, dificuldade, erro comum e retomada
- ser claro e útil
"""

def prompt_video(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """
Gere um Video Overview final sobre esse conteúdo.
Explique com clareza, linguagem natural, 2 exemplos progressivos, 1 erro comum com correção e fechamento curto de revisão.
Não faça roteiro para professor. Gere o material final do vídeo.
"""

def prompt_audio(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """
Gere um Audio Overview final para o responsável conduzir esse estudo.
Fale de forma prática e acolhedora, explicando o conteúdo, onde o aluno pode travar, como ajudar sem dar a resposta e como revisar no final.
Não faça roteiro técnico. Gere o material final do áudio.
"""

def prompt_slides(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """
Gere os slides finais desse estudo.
Pouco texto, boa clareza e progressão: conceito, exemplo, erro comum, aplicação e revisão.
Não faça instruções sobre slides. Gere o conteúdo final dos slides.
"""

def prompt_flash(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """
Gere os flashcards finais desse estudo.
Crie de 6 a 8 flashcards curtos com foco em conceito, aplicação, comparação e erro comum.
Não explique como fazer. Gere os flashcards prontos.
"""

def prompt_teste(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """
Gere um teste final curto e adaptado.
Crie 5 questões, com gabarito comentado e erros comuns esperados.
Não faça roteiro. Gere o teste pronto.
"""

def prompt_aula(data, materia, conteudo, estilo, situacao, prioridade, dias, selected, usa_fontes):
    parts = [
        contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes),
        "PACOTE DE AULA COMPLETA"
    ]
    if "Vídeo" in selected:
        parts.append("[VIDEO OVERVIEW]\n- gerar o material final do vídeo")
    if "Áudio (responsável)" in selected:
        parts.append("[AUDIO OVERVIEW]\n- gerar o material final do áudio para o responsável")
    if "Slides" in selected:
        parts.append("[SLIDES]\n- gerar os slides finais")
    if "Flashcards (máx 10)" in selected:
        parts.append("[FLASHCARDS]\n- gerar os flashcards prontos")
    if "Teste" in selected:
        parts.append("[TESTE]\n- gerar o teste pronto com gabarito")
    parts.append("Fechar com sinais de compreensão e sugestão breve de retomada.")
    return "\n\n".join(parts)

def prompt_cronograma(data, materia, conteudos, data_hoje, data_prova, alta, media, baixa):
    return f"""{build_base_prompt(data)}
CRONOGRAMA ATÉ A PROVA

Data de hoje: {data_hoje}
Data da prova: {data_prova}
Matéria: {materia}

Conteúdos da prova:
{conteudos}

Prioridade alta:
{alta}

Prioridade média:
{media}

Prioridade baixa:
{baixa}

Gere um plano por dia até a prova.
Para cada dia, usar exatamente este formato:

DIA X | DATA | CONTEÚDO DO DIA: ... | OBJETIVO: ... | ATIVIDADE: ... | REVISÃO: ... | TEXTO PARA COLAR EM "CONTEÚDO DO DIA": ...

Regras:
- máximo de 1 foco principal por dia
- sessões curtas
- incluir revisão final no dia anterior
- o campo TEXTO PARA COLAR EM "CONTEÚDO DO DIA" deve sair pronto para usar na aba Configuração
"""

def extrair_texto_para_conteudo_dia(linha):
    padrao = r'TEXTO PARA COLAR EM "CONTEÚDO DO DIA"\s*:\s*(.*)'
    match = re.search(padrao, linha, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return linha.strip()

# ======================
# ESTILO
# ======================

st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}
.card {
    padding: 16px 18px;
    border-radius: 18px;
    background: white;
    border: 1px solid rgba(15, 23, 42, 0.08);
    box-shadow: 0 6px 24px rgba(15, 23, 42, 0.05);
    margin-bottom: 12px;
}
.small {color: #475569; font-size: 0.92rem;}
h1, h2, h3 {color: #0f172a;}
hr {
    margin-top: 0.5rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ======================
# APP
# ======================

st.title("🧠 EduAI Studio - v6.3")
st.caption("Prompts mais curtos para o NotebookLM Studio, com campos clicáveis e cronograma reutilizável no conteúdo do dia.")

tabs = st.tabs(["👦 Perfil", "🧠 Aprendizagem", "🗓️ Cronograma", "⚙️ Configuração", "🎬 Studio", "📦 Aula Completa"])

# ======================
# TAB PERFIL
# ======================

with tabs[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Conhecendo a criança")
    c1, c2 = st.columns(2)
    st.session_state["nome"] = c1.text_input("Nome", value=st.session_state["nome"], key="perfil_nome_input")
    st.session_state["apelido"] = c2.text_input("Apelido", value=st.session_state["apelido"], key="perfil_apelido_input")
    st.session_state["idade"] = c1.text_input("Idade", value=st.session_state["idade"], key="perfil_idade_input")
    st.session_state["serie"] = c2.text_input("Série / Ano", value=st.session_state["serie"], key="perfil_serie_input")
    st.session_state["escola"] = c1.text_input("Escola", value=st.session_state["escola"], key="perfil_escola_input")
    st.session_state["turno"] = c2.text_input("Turno", value=st.session_state["turno"], key="perfil_turno_input")
    st.session_state["responsavel"] = st.text_input("Nome do responsável", value=st.session_state["responsavel"], key="perfil_responsavel_input")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Interesses")
    checkbox_group("Selecione os interesses da criança", INTERESSES_OPTIONS, "interesses", columns=4)
    if "Outro" in st.session_state["interesses"]:
        valor_outro_interesse = st.text_input(
            "Outro interesse",
            value=st.session_state.get("interesses_outro", ""),
            key="interesses_outro_input"
        )
        st.session_state["interesses_outro"] = valor_outro_interesse
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Diagnósticos e características")
    checkbox_group("Selecione um ou mais diagnósticos", DIAG_OPTIONS, "diagnosticos", columns=3)
    if "Outro" in st.session_state["diagnosticos"]:
        valor_outro_diag = st.text_input(
            "Qual outro diagnóstico?",
            value=st.session_state.get("outro_diagnostico", ""),
            key="outro_diag_input"
        )
        st.session_state["outro_diagnostico"] = valor_outro_diag

    if (not st.session_state["outras_caracteristicas"].strip()) or st.button("Atualizar características sugeridas", key="perfil_atualizar_caracteristicas_btn"):
        st.session_state["outras_caracteristicas"] = combine_characteristics(
            st.session_state["diagnosticos"],
            st.session_state.get("outro_diagnostico", "")
        )

    st.session_state["outras_caracteristicas"] = st.text_area(
        "Outras características (editável)",
        value=st.session_state["outras_caracteristicas"],
        height=120,
        key="perfil_outras_caracteristicas_textarea"
    )
    st.markdown('<div class="small">Essas informações alimentam automaticamente os prompts.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ======================
# TAB APRENDIZAGEM
# ======================

with tabs[1]:
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

    radio_group("Tipo de erro mais comum", ERRO_OPTIONS, "tipo_erro_mais_comum", horizontal=True)
    if st.session_state["tipo_erro_mais_comum"] == "Outro":
        valor_tipo_erro_outro = st.text_input(
            "Descreva o tipo de erro mais comum",
            value=st.session_state.get("tipo_erro_outro", ""),
            key="tipo_erro_outro_input"
        )
        st.session_state["tipo_erro_outro"] = valor_tipo_erro_outro

    st.markdown("<hr>", unsafe_allow_html=True)

    checkbox_group("O que mais engaja", ENGAJAMENTO_OPTIONS, "engajamento", columns=3)
    if "Outro" in st.session_state["engajamento"]:
        valor_engajamento_outro = st.text_input(
            "Outro fator de engajamento",
            value=st.session_state.get("engajamento_outro", ""),
            key="engajamento_outro_input"
        )
        st.session_state["engajamento_outro"] = valor_engajamento_outro

    checkbox_group("Principal dificuldade", DIFICULDADE_OPTIONS, "principal_dificuldade", columns=3)
    if "Outro" in st.session_state["principal_dificuldade"]:
        valor_dificuldade_outro = st.text_input(
            "Outra dificuldade observada",
            value=st.session_state.get("dificuldade_outro", ""),
            key="dificuldade_outro_input"
        )
        st.session_state["dificuldade_outro"] = valor_dificuldade_outro

    checkbox_group("Sinais quando trava", TRAVA_OPTIONS, "sinais_quando_trava", columns=3)
    if "Outro" in st.session_state["sinais_quando_trava"]:
        valor_trava_outro = st.text_input(
            "Outro sinal quando trava",
            value=st.session_state.get("trava_outro", ""),
            key="trava_outro_input"
        )
        st.session_state["trava_outro"] = valor_trava_outro

    checkbox_group("Melhor forma de retomar", RETOMADA_OPTIONS, "melhor_forma_retomar", columns=3)
    if "Outro" in st.session_state["melhor_forma_retomar"]:
        valor_retomada_outro = st.text_input(
            "Outra forma de retomar",
            value=st.session_state.get("retomada_outro", ""),
            key="retomada_outro_input"
        )
        st.session_state["retomada_outro"] = valor_retomada_outro

    st.markdown('<div class="small">Todos esses itens entram na interpretação dos prompts do Studio.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ======================
# TAB CRONOGRAMA
# ======================

with tabs[2]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Plano de estudo até a prova")

    st.session_state["cron_materia"] = st.text_input(
        "Matéria",
        value=st.session_state["cron_materia"],
        key="cron_materia_input"
    )

    hoje = st.date_input(
        "Data de hoje",
        value=datetime.date.today(),
        key="cron_hoje_input"
    )

    prova = st.date_input(
        "Data da prova",
        value=datetime.date.today(),
        key="cron_prova_input"
    )

    st.caption(f"Data de hoje: {formatar_data_br(hoje)}")
    st.caption(f"Data da prova: {formatar_data_br(prova)}")

    st.session_state["cron_conteudos"] = st.text_area(
        "Conteúdos da prova",
        value=st.session_state["cron_conteudos"],
        height=120,
        key="cron_conteudos_textarea"
    )

    a1, a2, a3 = st.columns(3)
    st.session_state["cron_alta"] = a1.text_area(
        "Prioridade alta",
        value=st.session_state["cron_alta"],
        height=110,
        key="cron_alta_textarea"
    )
    st.session_state["cron_media"] = a2.text_area(
        "Prioridade média",
        value=st.session_state["cron_media"],
        height=110,
        key="cron_media_textarea"
    )
    st.session_state["cron_baixa"] = a3.text_area(
        "Prioridade baixa",
        value=st.session_state["cron_baixa"],
        height=110,
        key="cron_baixa_textarea"
    )

    txt_cron = prompt_cronograma(
        get_perfil_data(formatar_data_br(prova)),
        st.session_state["cron_materia"],
        st.session_state["cron_conteudos"],
        formatar_data_br(hoje),
        formatar_data_br(prova),
        st.session_state["cron_alta"],
        st.session_state["cron_media"],
        st.session_state["cron_baixa"]
    )

    st.text_area(
        "Prompt de cronograma",
        value=txt_cron,
        height=360,
        key="cron_prompt_textarea"
    )

    st.markdown("**Usar a saída do cronograma na aba Configuração**")
    st.session_state["cronograma_linha_do_dia"] = st.text_area(
        "Cole aqui a linha do dia gerada no cronograma",
        value=st.session_state["cronograma_linha_do_dia"],
        height=90,
        key="cron_linha_dia_textarea"
    )

    if st.button("Usar essa linha no campo Conteúdo do dia", key="cron_usar_linha_btn"):
        st.session_state["conteudo_dia"] = extrair_texto_para_conteudo_dia(
            st.session_state["cronograma_linha_do_dia"]
        )
        st.success("Conteúdo do dia atualizado na aba Configuração.")

    st.markdown('</div>', unsafe_allow_html=True)

# ======================
# TAB CONFIGURAÇÃO
# ======================

with tabs[3]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Configuração didática do dia")

    st.session_state["mat_did"] = st.text_input(
        "Matéria",
        value=st.session_state["mat_did"],
        key="config_materia_input"
    )

    st.session_state["conteudo_dia"] = st.text_area(
        "Conteúdo do dia",
        value=st.session_state["conteudo_dia"],
        height=120,
        key="config_conteudo_dia_textarea"
    )

    st.session_state["objetivo_dia"] = st.text_input(
        "Objetivo do dia (opcional)",
        value=st.session_state["objetivo_dia"],
        key="config_objetivo_input"
    )

    hoje2 = st.date_input(
        "Data de hoje",
        value=datetime.date.today(),
        key="config_did_hoje"
    )

    prova2 = st.date_input(
        "Data da prova",
        value=datetime.date.today(),
        key="config_did_prova"
    )

    st.caption(f"Data de hoje: {formatar_data_br(hoje2)}")
    st.caption(f"Data da prova: {formatar_data_br(prova2)}")

    radio_group("Situação do conteúdo", SITUACAO_OPTIONS, "situacao_conteudo", horizontal=True)
    radio_group("Prioridade do conteúdo", PRIORIDADE_OPTIONS, "prioridade_conteudo", horizontal=True)

    st.session_state["usa_fontes"] = st.toggle(
        "Usar com fontes anexadas no NotebookLM",
        value=st.session_state["usa_fontes"],
        key="config_usa_fontes_toggle"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Como a escola cobra")
    checkbox_group("Selecione os formatos mais comuns", ESCOLA_COBRANCA_OPTIONS, "cobranca_escola", columns=3)
    if "Outro" in st.session_state["cobranca_escola"]:
        valor_cobranca_extra = st.text_input(
            "Outro tipo de cobrança",
            value=st.session_state.get("cobranca_extra", ""),
            key="cobranca_extra_input"
        )
        st.session_state["cobranca_extra"] = valor_cobranca_extra
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
        f"Modo sugerido: {modo_estudo((prova2 - hoje2).days, st.session_state['situacao_conteudo'])}"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Resumo do perfil atual")
    st.text_area(
        "Resumo estruturado",
        value=exportar_perfil_json(),
        height=240,
        key="config_resumo_textarea"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ======================
# TAB STUDIO
# ======================

with tabs[4]:
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
    conteudo = st.session_state["conteudo_dia"]
    situacao = st.session_state["situacao_conteudo"]
    prioridade = st.session_state["prioridade_conteudo"]

    st.subheader("Studio")
    st.caption("Prompts curtos para colar no NotebookLM Studio e gerar o material final.")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Vídeo")
        st.text_area(
            "Prompt de vídeo",
            value=prompt_video(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=220,
            key="studio_video_prompt"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Slides")
        st.text_area(
            "Prompt de slides",
            value=prompt_slides(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=220,
            key="studio_slides_prompt"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Flashcards")
        st.text_area(
            "Prompt de flashcards",
            value=prompt_flash(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=220,
            key="studio_flash_prompt"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Áudio do responsável")
        st.text_area(
            "Prompt de áudio",
            value=prompt_audio(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=240,
            key="studio_audio_prompt"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Teste")
        st.text_area(
            "Prompt de teste",
            value=prompt_teste(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=220,
            key="studio_teste_prompt"
        )
        st.markdown('</div>', unsafe_allow_html=True)

# ======================
# TAB AULA COMPLETA
# ======================

with tabs[5]:
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
    st.text_area(
        "Aula completa",
        value=aula,
        height=420,
        key="aula_completa_textarea"
    )
    st.markdown('</div>', unsafe_allow_html=True)
