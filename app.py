import streamlit as st
import datetime
import json

st.set_page_config(page_title="EduAI Studio", page_icon="🧠", layout="wide")

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
        "atenção curta", "beneficia-se de blocos curtos", "precisa de ritmo dinâmico",
        "responde melhor a objetivos claros e rápidos", "aprende melhor com estímulos visuais e interação"
    ],
    "TEA nível 1": [
        "beneficia-se de previsibilidade", "precisa de instruções claras e objetivas",
        "pode ter dificuldade com linguagem ambígua", "responde bem a rotinas estruturadas"
    ],
    "TEA nível 2": [
        "necessita maior estrutura e mediação", "precisa de previsibilidade e linguagem muito clara",
        "beneficia-se de passo a passo explícito", "pode demandar apoio mais frequente para transições"
    ],
    "TEA nível 3": [
        "necessita alto suporte", "precisa de linguagem simples, direta e previsível",
        "beneficia-se de rotinas muito estruturadas", "demanda mediação intensiva e apoio constante"
    ],
    "Dislexia": [
        "beneficia-se de menor carga textual", "precisa de frases mais curtas",
        "responde melhor a apoio visual", "pode cansar com leitura longa"
    ],
    "Discalculia": [
        "precisa de apoio concreto e visual", "beneficia-se de progressão muito gradual",
        "responde melhor a exemplos práticos", "pode travar diante de abstrações numéricas rápidas"
    ],
    "Processamento auditivo": [
        "beneficia-se de apoio visual constante", "pode ter dificuldade com instruções longas faladas",
        "precisa de mensagens curtas e objetivas", "responde melhor quando vê e ouve ao mesmo tempo"
    ],
    "Ansiedade": [
        "pode travar sob pressão", "precisa de segurança e progressão leve",
        "beneficia-se de previsibilidade e encorajamento objetivo", "responde melhor quando o erro é tratado com calma"
    ],
    "TOD": [
        "pode reagir melhor a linguagem neutra e respeitosa",
        "beneficia-se de escolhas simples e combinados claros",
        "responde melhor a estrutura firme sem confronto"
    ],
}

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
    "produção de resposta oral"
]

ATENCAO_OPTIONS = ["Muito baixa", "Baixa", "Média", "Boa"]
AUTONOMIA_OPTIONS = ["Precisa de muita mediação", "Precisa de alguma mediação", "Quase independente"]
CANAL_OPTIONS = ["Visual", "Auditivo", "Leitura guiada", "Manipulação/concreto", "Misto"]
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

DEFAULTS = {
    "nome": "",
    "apelido": "",
    "idade": "",
    "serie": "",
    "escola": "",
    "turno": "",
    "interesses": "",
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

    "engajamento": [],
    "engajamento_outro": "",
    "principal_dificuldade": [],
    "dificuldade_outro": "",
    "sinais_quando_trava": [],
    "trava_outro": "",
    "melhor_forma_retomar": [],
    "retomada_outro": "",
}

for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)

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

def obter_cobranca():
    vals = list(st.session_state["cobranca_escola"])
    extra = st.session_state["cobranca_extra"].strip()
    if extra:
        vals.append(extra)
    return ", ".join(vals)

def juntar_multiselect_com_outro(lista_base, texto_outro):
    itens = list(lista_base) if lista_base else []
    itens = [x for x in itens if x != "Outro"]
    if texto_outro and texto_outro.strip():
        itens.append(texto_outro.strip())
    return ", ".join(itens) if itens else "não informado"

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
- Tipo de erro mais comum: {st.session_state['tipo_erro_mais_comum']}
- Sinais quando trava: {trava}
- Melhor forma de retomar: {retomada}
""".strip()

def get_perfil_data(data_prova=""):
    return {
        "nome": st.session_state["nome"],
        "apelido": st.session_state["apelido"],
        "idade": st.session_state["idade"],
        "serie": st.session_state["serie"],
        "escola": st.session_state["escola"],
        "turno": st.session_state["turno"],
        "interesses": st.session_state["interesses"],
        "responsavel": st.session_state["responsavel"],
        "diagnosticos": st.session_state["diagnosticos"] + ([st.session_state["outro_diagnostico"]] if st.session_state["outro_diagnostico"] else []),
        "outras_caracteristicas": st.session_state["outras_caracteristicas"],
        "perfil_aprendizagem": perfil_aprendizagem_texto(),
        "data_prova": data_prova,
    }

def build_base_prompt(data):
    diags = ", ".join(data["diagnosticos"]) if data["diagnosticos"] else "Nenhum"
    return f"""PROFESSOR PARTICULAR

Você é um professor particular especializado em adaptação pedagógica e personalização de materiais para o perfil do aluno abaixo.

PERFIL DO ALUNO
Aluno: {data['nome']} ({data['apelido']})
Idade: {data['idade']}
Série: {data['serie']}
Escola: {data['escola']}
Turno: {data['turno']}
Responsável: {data['responsavel']}

DIAGNÓSTICOS INFORMADOS
{diags}

PERFIL DE APRENDIZAGEM
{data['perfil_aprendizagem']}

OUTRAS CARACTERÍSTICAS RELEVANTES
{data['outras_caracteristicas']}

INTERESSES
{data['interesses']}
"""

def contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    regras = (
        "- usar as fontes anexadas para extrair conceitos, vocabulário e estilo de cobrança\n"
        "- não copiar textos literalmente\n"
        "- não inventar páginas se elas não forem mencionadas"
        if usa_fontes else
        "- criar material mesmo sem fontes anexadas\n"
        "- usar conhecimento pedagógico compatível com a série\n"
        "- não citar páginas de livro"
    )
    return f"""{build_base_prompt(data)}
CONTEXTO
Matéria: {materia}
Conteúdo do dia: {conteudo}
Série: {data['serie']}
Data da prova: {data['data_prova']}
Dias restantes: {dias}
Situação do conteúdo: {situacao}
Prioridade: {prioridade}
Modo de estudo: {modo_estudo(dias, situacao)}
Forma de cobrança da escola:
{estilo or 'não informada'}
Modo de uso:
{'com fontes anexadas' if usa_fontes else 'sem fontes anexadas'}

IMPORTANTE
{regras}
- não copiar exercícios
- criar exemplos inéditos
- adaptar tudo ao perfil do aluno
"""

def resumo_aluno_compacto(data):
    diags = ", ".join(data["diagnosticos"]) if data["diagnosticos"] else "nenhum"

    perfil_curto = (
        f"Atenção: {st.session_state.get('atencao_sustentada', 'não informado')}; "
        f"Autonomia: {st.session_state.get('autonomia', 'não informado')}; "
        f"Canal: {st.session_state.get('canal_preferencial', 'não informado')}; "
        f"Engaja com: {juntar_multiselect_com_outro(st.session_state['engajamento'], st.session_state['engajamento_outro'])}; "
        f"Dificuldade: {juntar_multiselect_com_outro(st.session_state['principal_dificuldade'], st.session_state['dificuldade_outro'])}; "
        f"Quando trava: {juntar_multiselect_com_outro(st.session_state['sinais_quando_trava'], st.session_state['trava_outro'])}; "
        f"Retomar: {juntar_multiselect_com_outro(st.session_state['melhor_forma_retomar'], st.session_state['retomada_outro'])}"
    )

    return (
        f"Aluno: {data['nome'] or 'não informado'}, "
        f"{data['idade'] or '?'} anos, {data['serie'] or 'série não informada'}. "
        f"Diagnósticos: {diags}. "
        f"Perfil: {perfil_curto}. "
        f"Interesses: {data['interesses'] or 'não informado'}."
    )

def contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    modo_fontes = "usar as fontes anexadas como base" if usa_fontes else "criar sem depender de fontes anexadas"

    return f"""Crie material de estudo personalizado.
Contexto:
- Matéria: {materia}
- Conteúdo: {conteudo}
- Dias até a prova: {dias}
- Situação: {situacao}
- Prioridade: {prioridade}
- Como a escola cobra: {estilo or 'não informado'}
- Modo: {modo_fontes}

Perfil do aluno:
{resumo_aluno_compacto(data)}

Regras:
- ser claro, direto e pedagógico
- adaptar à idade, série e perfil
- não repetir todo o perfil ao longo da resposta
- não enrolar
- não infantilizar demais
- criar material realmente útil para estudo
"""

def prompt_video(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """

Gere um roteiro de vídeo curto com:
1. objetivo da explicação
2. abertura com gancho
3. explicação em etapas
4. 2 exemplos progressivos
5. 2 perguntas para interação
6. 1 erro comum com correção
7. mini fechamento com revisão

Use linguagem falada, natural e memorável.
"""

def prompt_audio(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """

Gere um roteiro de áudio para o responsável com:
1. objetivo da sessão
2. como começar
3. como explicar sem complicar
4. onde o aluno pode travar
5. como ajudar sem dar a resposta
6. frases curtas que o responsável pode usar
7. como encerrar e revisar

Seja prático, acolhedor e direto.
"""

def prompt_slides(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """

Gere uma sequência curta de slides de estudo.
Para cada slide, traga:
- título
- conteúdo principal
- sugestão visual
- fala de apoio

Estrutura:
1. abertura
2. conceito principal
3. exemplo
4. erro comum
5. aplicação rápida
6. revisão final

Pouco texto, boa clareza e progressão lógica.
"""

def prompt_flash(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """

Gere de 6 a 8 flashcards.
Para cada um, traga:
- frente
- verso
- tipo: conceito, aplicação, comparação ou erro comum

Regras:
- não passar de 8
- variar as perguntas
- focar no que mais ajuda a lembrar e acertar
"""

def prompt_teste(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """

Gere um teste curto e adaptado.
Entregue:
1. 5 questões
2. gabarito comentado
3. erros comuns esperados

Regras:
- alinhar ao modo como a escola cobra
- misturar fácil, médio e 1 desafio leve
- ser claro e objetivo
"""

def prompt_aula(data, materia, conteudo, estilo, situacao,prioridade,dias,selected,usa_fontes):
    parts = [contexto_geral(data,materia,conteudo,estilo,situacao,prioridade,dias,usa_fontes),"AULA COMPLETA - PACOTE DE MATERIAIS"]
    if "Vídeo" in selected:
        parts.append("[VIDEO OVERVIEW]\n- criar roteiro curto, visual e didático")
    if "Áudio (responsável)" in selected:
        parts.append("[AUDIO OVERVIEW PARA O RESPONSÁVEL]\n- orientar a condução da aula")
    if "Slides" in selected:
        parts.append("[SLIDES]\n- organizar em poucos slides")
    if "Flashcards (máx 10)" in selected:
        parts.append("[FLASHCARDS]\n- gerar entre 5 e 10 itens, máximo 10")
    if "Teste" in selected:
        parts.append("[TESTE]\n- criar avaliação curta com gabarito")
    return "\n\n".join(parts)

def prompt_cronograma(data,materia,conteudos,data_hoje,data_prova,alta,media,baixa):
    return f"""{build_base_prompt(data)}
PROMPT - CRONOGRAMA COMPLETO ATÉ A PROVA

CONTEXTO ATUAL
Data de hoje: {data_hoje}
Data da prova: {data_prova}
Matéria: {materia}
Série: {data['serie']}

CONTEÚDOS DA PROVA
{conteudos}

PRIORIDADE
Alta:
{alta}

Média:
{media}

Baixa:
{baixa}

REGRAS DE PLANEJAMENTO
- dividir o estudo por dias até a prova
- sessões de 15 a 25 minutos
- máximo de 1 conteúdo principal por dia
- incluir revisão final no dia anterior
- não detalhar a aula
- gerar o plano completo
"""

def exportar_perfil_json():
    data = get_perfil_data()
    return json.dumps(data, ensure_ascii=False, indent=2)

st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
[data-testid="stAppViewContainer"] {background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);}
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
</style>
""", unsafe_allow_html=True)

st.title("🧠 EduAI Studio - v6.2")
st.caption("Perfil preservado, aprendizagem refinada e prompts do Studio mais compactos para o NotebookLM.")

tabs = st.tabs(["👦 Perfil", "🧠 Aprendizagem", "🗓️ Cronograma", "⚙️ Configuração", "🎬 Studio", "📦 Aula Completa"])

with tabs[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Conhecendo a criança")
    c1, c2 = st.columns(2)
    st.session_state["nome"] = c1.text_input("Nome", value=st.session_state["nome"])
    st.session_state["apelido"] = c2.text_input("Apelido", value=st.session_state["apelido"])
    st.session_state["idade"] = c1.text_input("Idade", value=st.session_state["idade"])
    st.session_state["serie"] = c2.text_input("Série / Ano", value=st.session_state["serie"])
    st.session_state["escola"] = c1.text_input("Escola", value=st.session_state["escola"])
    st.session_state["turno"] = c2.text_input("Turno", value=st.session_state["turno"])
    st.session_state["interesses"] = st.text_area("Interesses", value=st.session_state["interesses"], height=90)
    st.session_state["responsavel"] = st.text_input("Nome do responsável", value=st.session_state["responsavel"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Diagnósticos e características")
    st.session_state["diagnosticos"] = st.multiselect(
        "Selecione um ou mais diagnósticos",
        DIAG_OPTIONS,
        default=st.session_state["diagnosticos"]
    )
    if "Outro" in st.session_state["diagnosticos"]:
        st.session_state["outro_diagnostico"] = st.text_input(
            "Qual outro diagnóstico?",
            value=st.session_state["outro_diagnostico"],
            key="outro_diag_input"
        )
    else:
        st.session_state["outro_diagnostico"] = ""

    if (not st.session_state["outras_caracteristicas"].strip()) or st.button("Atualizar características sugeridas"):
        st.session_state["outras_caracteristicas"] = combine_characteristics(
            st.session_state["diagnosticos"],
            st.session_state["outro_diagnostico"]
        )

    st.session_state["outras_caracteristicas"] = st.text_area(
        "Outras características (editável)",
        value=st.session_state["outras_caracteristicas"],
        height=120
    )
    st.markdown('<div class="small">O perfil fica salvo na própria página enquanto você estiver usando o app.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Perfil de aprendizagem refinado")

    a1, a2, a3 = st.columns(3)
    st.session_state["atencao_sustentada"] = a1.selectbox(
        "Atenção sustentada",
        ATENCAO_OPTIONS,
        index=ATENCAO_OPTIONS.index(st.session_state["atencao_sustentada"]) if st.session_state["atencao_sustentada"] in ATENCAO_OPTIONS else 2
    )
    st.session_state["autonomia"] = a2.selectbox(
        "Autonomia",
        AUTONOMIA_OPTIONS,
        index=AUTONOMIA_OPTIONS.index(st.session_state["autonomia"]) if st.session_state["autonomia"] in AUTONOMIA_OPTIONS else 1
    )
    st.session_state["canal_preferencial"] = a3.selectbox(
        "Canal preferencial",
        CANAL_OPTIONS,
        index=CANAL_OPTIONS.index(st.session_state["canal_preferencial"]) if st.session_state["canal_preferencial"] in CANAL_OPTIONS else 0
    )

    b1, b2, b3, b4 = st.columns(4)
    st.session_state["tolerancia_frustracao"] = b1.selectbox(
        "Tolerância à frustração",
        FRUSTRACAO_OPTIONS,
        index=FRUSTRACAO_OPTIONS.index(st.session_state["tolerancia_frustracao"]) if st.session_state["tolerancia_frustracao"] in FRUSTRACAO_OPTIONS else 1
    )
    st.session_state["leitura_nivel"] = b2.selectbox(
        "Leitura",
        NIVEL_OPTIONS,
        index=NIVEL_OPTIONS.index(st.session_state["leitura_nivel"]) if st.session_state["leitura_nivel"] in NIVEL_OPTIONS else 1
    )
    st.session_state["escrita_nivel"] = b3.selectbox(
        "Escrita",
        NIVEL_OPTIONS,
        index=NIVEL_OPTIONS.index(st.session_state["escrita_nivel"]) if st.session_state["escrita_nivel"] in NIVEL_OPTIONS else 1
    )
    st.session_state["matematica_nivel"] = b4.selectbox(
        "Matemática",
        NIVEL_OPTIONS,
        index=NIVEL_OPTIONS.index(st.session_state["matematica_nivel"]) if st.session_state["matematica_nivel"] in NIVEL_OPTIONS else 1
    )

    c1, c2 = st.columns(2)
    st.session_state["compreensao_oral"] = c1.selectbox(
        "Compreensão oral",
        ["Baixa", "Média", "Boa"],
        index=["Baixa", "Média", "Boa"].index(st.session_state["compreensao_oral"]) if st.session_state["compreensao_oral"] in ["Baixa", "Média", "Boa"] else 1
    )
    st.session_state["tipo_erro_mais_comum"] = c2.selectbox(
        "Tipo de erro mais comum",
        ERRO_OPTIONS,
        index=ERRO_OPTIONS.index(st.session_state["tipo_erro_mais_comum"]) if st.session_state["tipo_erro_mais_comum"] in ERRO_OPTIONS else 0
    )

    st.markdown("### O que mais engaja")
    st.session_state["engajamento"] = st.multiselect(
        "Selecione uma ou mais opções de engajamento",
        ENGAJAMENTO_OPTIONS,
        default=st.session_state["engajamento"],
        key="engajamento_multiselect"
    )
    if "Outro" in st.session_state["engajamento"]:
        st.session_state["engajamento_outro"] = st.text_input(
            "Outro fator de engajamento",
            value=st.session_state["engajamento_outro"],
            key="engajamento_outro_input"
        )
    else:
        st.session_state["engajamento_outro"] = ""

    st.markdown("### Principal dificuldade")
    st.session_state["principal_dificuldade"] = st.multiselect(
        "Selecione uma ou mais dificuldades",
        DIFICULDADE_OPTIONS,
        default=st.session_state["principal_dificuldade"],
        key="dificuldade_multiselect"
    )
    if "Outro" in st.session_state["principal_dificuldade"]:
        st.session_state["dificuldade_outro"] = st.text_input(
            "Outra dificuldade observada",
            value=st.session_state["dificuldade_outro"],
            key="dificuldade_outro_input"
        )
    else:
        st.session_state["dificuldade_outro"] = ""

    st.markdown("### Sinais quando trava")
    st.session_state["sinais_quando_trava"] = st.multiselect(
        "Selecione um ou mais sinais",
        TRAVA_OPTIONS,
        default=st.session_state["sinais_quando_trava"],
        key="trava_multiselect"
    )
    if "Outro" in st.session_state["sinais_quando_trava"]:
        st.session_state["trava_outro"] = st.text_input(
            "Outro sinal quando trava",
            value=st.session_state["trava_outro"],
            key="trava_outro_input"
        )
    else:
        st.session_state["trava_outro"] = ""

    st.markdown("### Melhor forma de retomar")
    st.session_state["melhor_forma_retomar"] = st.multiselect(
        "Selecione uma ou mais formas de retomada",
        RETOMADA_OPTIONS,
        default=st.session_state["melhor_forma_retomar"],
        key="retomada_multiselect"
    )
    if "Outro" in st.session_state["melhor_forma_retomar"]:
        st.session_state["retomada_outro"] = st.text_input(
            "Outra forma de retomar",
            value=st.session_state["retomada_outro"],
            key="retomada_outro_input"
        )
    else:
        st.session_state["retomada_outro"] = ""

    st.markdown('<div class="small">Essas informações ajudam a IA a ajustar linguagem, ritmo, mediação e tipo de atividade.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Plano de estudo até a prova")
    materia_cron = st.text_input("Matéria", key="materia_cron")
    hoje = st.date_input("Data de hoje", value=datetime.date.today(), key="cron_hoje")
    prova = st.date_input("Data da prova", value=datetime.date.today(), key="cron_prova")
    conteudos = st.text_area("Conteúdos da prova", height=120, key="conteudos_prova")
    a1, a2, a3 = st.columns(3)
    alta = a1.text_area("Prioridade alta", height=110, key="alta")
    media = a2.text_area("Prioridade média", height=110, key="media")
    baixa = a3.text_area("Prioridade baixa", height=110, key="baixa")
    st.caption(f"Prova marcada para {formatar_data_extenso(prova)}.")
    txt = prompt_cronograma(
        get_perfil_data(formatar_data_br(prova)),
        materia_cron,
        conteudos,
        formatar_data_br(hoje),
        formatar_data_br(prova),
        alta,
        media,
        baixa
    )
    st.text_area("Prompt de cronograma", value=txt, height=280)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[3]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Configuração didática do dia")
    materia = st.text_input("Matéria", key="mat_did")
    conteudo = st.text_input("Conteúdo do dia", key="conteudo_dia")
    hoje2 = st.date_input("Data de hoje", value=datetime.date.today(), key="did_hoje")
    prova2 = st.date_input("Data da prova", value=datetime.date.today(), key="did_prova")
    situacao = st.selectbox("Situação do conteúdo", ["novo", "ja_visto", "em_dificuldade"], index=0)
    prioridade = st.selectbox("Prioridade do conteúdo", ["alta", "media", "baixa"], index=0)
    st.session_state["usa_fontes"] = st.toggle("Usar com fontes anexadas no NotebookLM", value=st.session_state["usa_fontes"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Como a escola cobra")
    st.session_state["cobranca_escola"] = st.multiselect(
        "Selecione os formatos mais comuns",
        ESCOLA_COBRANCA_OPTIONS,
        default=st.session_state["cobranca_escola"]
    )
    st.session_state["cobranca_extra"] = st.text_input(
        "Outro tipo de cobrança (opcional)",
        value=st.session_state["cobranca_extra"]
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Materiais")
    st.session_state["selected_materials"] = st.multiselect(
        "Escolha os materiais",
        ["Vídeo", "Áudio (responsável)", "Slides", "Flashcards (máx 10)", "Teste"],
        default=st.session_state["selected_materials"]
    )
    st.info(f"Dias até a prova: {(prova2 - hoje2).days} | Modo sugerido: {modo_estudo((prova2 - hoje2).days, situacao)}")
    st.caption(f"Prova marcada para {formatar_data_extenso(prova2)}.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Resumo do perfil atual")
    st.text_area("Resumo estruturado", value=exportar_perfil_json(), height=220)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[4]:
    try:
        days = (prova2 - hoje2).days
        estilo = obter_cobranca()
    except Exception:
        days = 0
        materia = conteudo = estilo = ""
        situacao = "novo"
        prioridade = "media"
        prova2 = datetime.date.today()

    perfil = get_perfil_data(formatar_data_br(prova2))
    usa = st.session_state["usa_fontes"]

    st.subheader("Studio")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Vídeo")
        st.text_area(
            "Prompt de vídeo",
            value=prompt_video(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=210
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Slides")
        st.text_area(
            "Prompt de slides",
            value=prompt_slides(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=230
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Flashcards")
        st.text_area(
            "Prompt de flashcards",
            value=prompt_flash(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=210
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Áudio do responsável")
        st.text_area(
            "Prompt de áudio",
            value=prompt_audio(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=220
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Teste")
        st.text_area(
            "Prompt de teste",
            value=prompt_teste(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=210
        )
        st.markdown('</div>', unsafe_allow_html=True)

with tabs[5]:
    try:
        days = (prova2 - hoje2).days
        estilo = obter_cobranca()
    except Exception:
        days = 0
        materia = conteudo = estilo = ""
        situacao = "novo"
        prioridade = "media"
        prova2 = datetime.date.today()

    perfil = get_perfil_data(formatar_data_br(prova2))
    aula = prompt_aula(
        perfil, materia, conteudo, estilo, situacao, prioridade,
        days, st.session_state["selected_materials"], st.session_state["usa_fontes"]
    )
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Pacote de aula completa")
    st.text_area("Aula completa", value=aula, height=360)
    st.markdown('</div>', unsafe_allow_html=True)
