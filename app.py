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
    "caracteristicas_sugeridas": "",

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
# MIGRAÇÃO DE CHAVES ANTIGAS
# ======================

LEGACY_KEY_MAP = {
    "perfil_nome_input": "nome",
    "perfil_apelido_input": "apelido",
    "perfil_idade_input": "idade",
    "perfil_serie_input": "serie",
    "perfil_escola_input": "escola",
    "perfil_turno_input": "turno",
    "perfil_responsavel_input": "responsavel",
    "config_materia_input": "mat_did",
    "config_conteudo_dia_textarea": "conteudo_dia",
    "config_objetivo_input": "objetivo_dia",
    "cron_materia_input": "cron_materia",
    "cron_conteudos_textarea": "cron_conteudos",
    "cron_alta_textarea": "cron_alta",
    "cron_media_textarea": "cron_media",
    "cron_baixa_textarea": "cron_baixa",
}

for old_key, new_key in LEGACY_KEY_MAP.items():
    old_val = st.session_state.get(old_key, "")
    new_val = st.session_state.get(new_key, "")
    if (not new_val) and old_val:
        st.session_state[new_key] = old_val

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

def atualizar_caracteristicas_sugeridas():
    st.session_state["caracteristicas_sugeridas"] = combine_characteristics(
        st.session_state["diagnosticos"],
        st.session_state.get("outro_diagnostico", "")
    )

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

    atualizar_caracteristicas_sugeridas()

    outras = st.session_state["outras_caracteristicas"].strip()
    sugeridas = st.session_state["caracteristicas_sugeridas"].strip()

    bloco_caracteristicas = sugeridas
    if outras:
        bloco_caracteristicas = f"{sugeridas}; {outras}" if sugeridas else outras

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
        "outras_caracteristicas": bloco_caracteristicas,
        "caracteristicas_sugeridas": sugeridas,
        "perfil_aprendizagem": perfil_aprendizagem_texto(),
        "data_prova": data_prova,
    }

def exportar_perfil_json():
    data = get_perfil_data()
    return json.dumps(data, ensure_ascii=False, indent=2)

def resumo_aluno_compacto(data):
    diags = ", ".join(data["diagnosticos"]) if data["diagnosticos"] else "nenhum"

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

    return f"""ALUNO
- Nome: {data['nome'] or 'não informado'}
- Apelido: {data['apelido'] or 'não informado'}
- Idade: {data['idade'] or 'não informado'}
- Série: {data['serie'] or 'não informada'}
- Escola: {data['escola'] or 'não informada'}
- Turno: {data['turno'] or 'não informado'}
- Responsável: {data['responsavel'] or 'não informado'}

DIAGNÓSTICOS
- {diags}

INTERESSES
- {data['interesses'] or 'não informado'}

CARACTERÍSTICAS SUGERIDAS DO DIAGNÓSTICO
- {data.get('caracteristicas_sugeridas', '') or 'não informado'}

PERFIL DE APRENDIZAGEM
- Atenção sustentada: {st.session_state['atencao_sustentada']}
- Autonomia: {st.session_state['autonomia']}
- Canal preferencial: {st.session_state['canal_preferencial']}
- Tolerância à frustração: {st.session_state['tolerancia_frustracao']}
- Leitura: {st.session_state['leitura_nivel']}
- Escrita: {st.session_state['escrita_nivel']}
- Matemática: {st.session_state['matematica_nivel']}
- Compreensão oral: {st.session_state['compreensao_oral']}
- O que mais engaja: {engajamento}
- Principal dificuldade: {dificuldade}
- Tipo de erro mais comum: {obter_tipo_erro()}
- Sinais quando trava: {trava}
- Melhor forma de retomar: {retomada}

OUTRAS CARACTERÍSTICAS
- {st.session_state['outras_caracteristicas'] or 'não informado'}
"""

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

CARACTERÍSTICAS SUGERIDAS DO DIAGNÓSTICO
{data.get('caracteristicas_sugeridas', 'não informado') or 'não informado'}

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
    modo_fontes = "usar as fontes anexadas como base principal" if usa_fontes else "criar sem depender de fontes anexadas"
    objetivo_dia = st.session_state.get("objetivo_dia", "").strip() or "não informado"

    return f"""CRIE O MATERIAL FINAL PARA O NOTEBOOKLM STUDIO.

CONTEXTO DO ESTUDO
- Matéria: {materia or 'não informada'}
- Conteúdo do dia: {conteudo or 'não informado'}
- Objetivo do dia: {objetivo_dia}
- Dias até a prova: {dias}
- Situação do conteúdo: {situacao}
- Prioridade: {prioridade}
- Como a escola cobra: {estilo or 'não informado'}
- Modo de uso: {modo_fontes}

DADOS DO ALUNO
{resumo_aluno_compacto(data)}

REGRAS GERAIS
- usar TODAS as informações acima para adaptar o material
- considerar idade, série, diagnósticos, características sugeridas do diagnóstico, interesses, engajamento, dificuldade, erro comum e retomada
- alinhar o material ao jeito que a escola cobra
- ser claro, útil e direto
- não explicar como fazer o material
- gerar o material final pronto para uso
"""

def prompt_video(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """
Crie o VIDEO OVERVIEW final, pronto para uso.
Explique o conteúdo de forma clara, envolvente e adaptada ao aluno.
Inclua exemplos alinhados ao perfil e interesses do aluno, trate o erro comum esperado e finalize com revisão breve.
Saída final pronta para o Studio.
"""

def prompt_audio(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """
Crie o AUDIO OVERVIEW final, pronto para uso pelo responsável.
Explique como conduzir esse conteúdo com esse aluno, onde ele pode travar, como retomar e como revisar.
Use linguagem natural, prática e acolhedora.
Saída final pronta para o Studio.
"""

def prompt_slides(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """
Crie os SLIDES finais do estudo.
Organize com progressão clara: conceito, exemplo, erro comum, aplicação e revisão.
Use pouco texto por slide e linguagem adequada ao aluno.
Saída final pronta para o Studio.
"""

def prompt_flash(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """
Crie os FLASHCARDS finais.
Gere de 6 a 8 flashcards úteis para esse aluno, com foco em conceito, aplicação, comparação e erro comum.
Saída final pronta para o Studio.
"""

def prompt_teste(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """
Crie o TESTE final.
Gere 5 questões adaptadas ao aluno e ao formato de cobrança da escola, com gabarito comentado e erros comuns esperados.
Saída final pronta para o Studio.
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

def extrair_campos_cronograma(linha):
    resultado = {
        "conteudo": "",
        "objetivo": "",
        "atividade": "",
        "revisao": "",
        "texto_colar": ""
    }

    padroes = {
        "conteudo": r"CONTEÚDO DO DIA:\s*(.*?)\s*(?:\||$)",
        "objetivo": r"OBJETIVO:\s*(.*?)\s*(?:\||$)",
        "atividade": r"ATIVIDADE:\s*(.*?)\s*(?:\||$)",
        "revisao": r"REVISÃO:\s*(.*?)\s*(?:\||$)",
        "texto_colar": r'TEXTO PARA COLAR EM "CONTEÚDO DO DIA":\s*(.*)'
    }

    for chave, padrao in padroes.items():
        match = re.search(padrao, linha, flags=re.IGNORECASE)
        if match:
            resultado[chave] = match.group(1).strip()

    return resultado

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

st.title("🧠 EduAI Studio - v6.6")
st.caption("Características do diagnóstico visíveis e usadas nos prompts, com migração embutida.")

tabs = st.tabs(["👦 Perfil", "🧠 Aprendizagem", "🗓️ Cronograma", "⚙️ Configuração", "🎬 Studio", "📦 Aula Completa"])

# ======================
# TAB PERFIL
# ======================

with tabs[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Conhecendo a criança")
    c1, c2 = st.columns(2)

    st.session_state["nome"] = c1.text_input("Nome", value=st.session_state.get("nome", ""), key="nome")
    st.session_state["apelido"] = c2.text_input("Apelido", value=st.session_state.get("apelido", ""), key="apelido")
    st.session_state["idade"] = c1.text_input("Idade", value=st.session_state.get("idade", ""), key="idade")
    st.session_state["serie"] = c2.text_input("Série / Ano", value=st.session_state.get("serie", ""), key="serie")
    st.session_state["escola"] = c1.text_input("Escola", value=st.session_state.get("escola", ""), key="escola")
    st.session_state["turno"] = c2.text_input("Turno", value=st.session_state.get("turno", ""), key="turno")
    st.session_state["responsavel"] = st.text_input("Nome do responsável", value=st.session_state.get("responsavel", ""), key="responsavel")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Interesses")
    checkbox_group("Selecione os interesses da criança", INTERESSES_OPTIONS, "interesses", columns=4)
    if "Outro" in st.session_state["interesses"]:
        st.session_state["interesses_outro"] = st.text_input(
            "Outro interesse",
            value=st.session_state.get("interesses_outro", ""),
            key="interesses_outro"
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Diagnósticos e características")
    checkbox_group("Selecione um ou mais diagnósticos", DIAG_OPTIONS, "diagnosticos", columns=3)

    if "Outro" in st.session_state["diagnosticos"]:
        st.session_state["outro_diagnostico"] = st.text_input(
            "Qual outro diagnóstico?",
            value=st.session_state.get("outro_diagnostico", ""),
            key="outro_diagnostico"
        )

    atualizar_caracteristicas_sugeridas()

    st.text_area(
        "Características sugeridas automaticamente pelos diagnósticos",
        value=st.session_state.get("caracteristicas_sugeridas", ""),
        height=120,
        key="caracteristicas_sugeridas_exibicao",
        disabled=True
    )

    st.session_state["outras_caracteristicas"] = st.text_area(
        "Outras características (editável)",
        value=st.session_state.get("outras_caracteristicas", ""),
        key="outras_caracteristicas",
        height=120
    )

    st.markdown('<div class="small">As características sugeridas dos diagnósticos e as características adicionais entram nos prompts.</div>', unsafe_allow_html=True)
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

    st.markdown('<div class="small">Todos esses itens entram na interpretação dos prompts do Studio.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ======================
# TAB CRONOGRAMA
# ======================

with tabs[2]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Plano de estudo até a prova")

    st.text_input("Matéria", key="cron_materia")

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

    st.text_area(
        "Conteúdos da prova",
        key="cron_conteudos",
        height=120
    )

    a1, a2, a3 = st.columns(3)
    a1.text_area("Prioridade alta", key="cron_alta", height=110)
    a2.text_area("Prioridade média", key="cron_media", height=110)
    a3.text_area("Prioridade baixa", key="cron_baixa", height=110)

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
    st.text_area(
        "Cole aqui a linha do dia gerada no cronograma",
        key="cronograma_linha_do_dia",
        height=90
    )

    if st.button("Usar essa linha na aba Configuração", key="cron_usar_linha_btn"):
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

        st.success("Matéria, conteúdo do dia e objetivo foram enviados para a aba Configuração.")

    st.markdown('</div>', unsafe_allow_html=True)

# ======================
# TAB CONFIGURAÇÃO
# ======================

with tabs[3]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Configuração didática do dia")

    st.text_input("Matéria", key="mat_did")

    st.text_area(
        "Conteúdo do dia",
        key="conteudo_dia",
        height=120
    )

    st.text_input(
        "Objetivo do dia (opcional)",
        key="objetivo_dia"
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

    st.toggle(
        "Usar com fontes anexadas no NotebookLM",
        key="usa_fontes"
    )
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

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Base usada nos prompts")
    base_prompt_studio = contexto_studio_compacto(
        perfil, materia, conteudo, estilo, situacao, prioridade, days, usa
    )
    st.text_area(
        "Base real enviada para os prompts",
        value=base_prompt_studio,
        height=340,
        key="studio_base_real_textarea"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Vídeo")
        st.text_area(
            "Prompt de vídeo",
            value=prompt_video(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=230,
            key="studio_video_prompt"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Slides")
        st.text_area(
            "Prompt de slides",
            value=prompt_slides(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=230,
            key="studio_slides_prompt"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Flashcards")
        st.text_area(
            "Prompt de flashcards",
            value=prompt_flash(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=230,
            key="studio_flash_prompt"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Áudio do responsável")
        st.text_area(
            "Prompt de áudio",
            value=prompt_audio(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=250,
            key="studio_audio_prompt"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Teste")
        st.text_area(
            "Prompt de teste",
            value=prompt_teste(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=230,
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
