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
        "atenção oscilante", "beneficia-se de blocos curtos", "precisa de ritmo dinâmico",
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
    ]
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

INTENSIDADE_OPTIONS = ["Essencial", "Forte", "Profundo", "Prova difícil"]

ATENCAO_OPTIONS = ["Muito baixa", "Baixa", "Média", "Boa"]
AUTONOMIA_OPTIONS = ["Precisa de muita mediação", "Precisa de alguma mediação", "Quase independente"]
CANAL_OPTIONS = ["Visual", "Auditivo", "Leitura guiada", "Manipulação/concreto", "Misto"]
FRUSTRACAO_OPTIONS = ["Baixa", "Média", "Boa"]
NIVEL_OPTIONS = ["Abaixo do esperado", "Adequado", "Acima do esperado"]
ERRO_OPTIONS = ["Trava", "Chuta", "Dispersa", "Fica ansioso", "Recusa", "Outro"]
SITUACAO_OPTIONS = ["novo", "ja_visto", "em_dificuldade"]
PRIORIDADE_OPTIONS = ["alta", "media", "baixa"]

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
    "intensidade": "Forte",

    "atencao_sustentada": "Média",
    "autonomia": "Precisa de alguma mediação",
    "canal_preferencial": "Visual",
    "tolerancia_frustracao": "Média",
    "leitura_nivel": "Adequado",
    "escrita_nivel": "Adequado",
    "matematica_nivel": "Adequado",
    "compreensao_oral": "Média",
    "engajamento": "",
    "principal_dificuldade": "",
    "tipo_erro_mais_comum": "Trava",
    "sinais_quando_trava": "",
    "melhor_forma_retomar": ""
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
    items = []
    seen = set()
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

def perfil_aprendizagem_texto():
    return f"""
- Atenção sustentada: {st.session_state['atencao_sustentada']}
- Autonomia: {st.session_state['autonomia']}
- Canal preferencial: {st.session_state['canal_preferencial']}
- Tolerância à frustração: {st.session_state['tolerancia_frustracao']}
- Leitura: {st.session_state['leitura_nivel']}
- Escrita: {st.session_state['escrita_nivel']}
- Matemática: {st.session_state['matematica_nivel']}
- Compreensão oral: {st.session_state['compreensao_oral']}
- Forma de engajamento que funciona melhor: {st.session_state['engajamento'] or 'não informada'}
- Principal dificuldade observada: {st.session_state['principal_dificuldade'] or 'não informada'}
- Tipo de erro mais comum: {st.session_state['tipo_erro_mais_comum']}
- Sinais quando trava: {st.session_state['sinais_quando_trava'] or 'não informado'}
- Melhor forma de retomar: {st.session_state['melhor_forma_retomar'] or 'não informada'}
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
        "interesses": st.session_state["interesses"],
        "responsavel": st.session_state["responsavel"],
        "diagnosticos": diagnosticos,
        "outras_caracteristicas": st.session_state["outras_caracteristicas"],
        "perfil_aprendizagem": perfil_aprendizagem_texto(),
        "data_prova": data_prova,
        "intensidade": st.session_state["intensidade"]
    }

def intensidade_instrucao(intensidade):
    mapa = {
        "Essencial": """
NÍVEL DE PROFUNDIDADE
- ser direto, claro e funcional
- trabalhar o núcleo do conteúdo
- reduzir excesso de detalhes
- priorizar compreensão básica + segurança
""",
        "Forte": """
NÍVEL DE PROFUNDIDADE
- gerar material completo e consistente
- incluir progressão clara, exemplos bem construídos e checagem de compreensão
- aprofundar sem ficar pesado
""",
        "Profundo": """
NÍVEL DE PROFUNDIDADE
- gerar material mais robusto, comparativo e explicativo
- incluir nuances, conexões entre ideias e múltiplos exemplos
- reforçar raciocínio, aplicação e retenção
""",
        "Prova difícil": """
NÍVEL DE PROFUNDIDADE
- preparar para cobrança mais exigente
- incluir inferência, aplicação, armadilhas comuns e comparação entre conceitos
- elevar a exigência sem perder clareza
"""
    }
    return mapa.get(intensidade, mapa["Forte"])

def build_base_prompt(data):
    diags = ", ".join(data["diagnosticos"]) if data["diagnosticos"] else "Nenhum"

    return f"""IDENTIDADE DO ESPECIALISTA
Você é um especialista em aprendizagem personalizada, adaptação pedagógica, neuroaprendizagem, design instrucional e elaboração de materiais de estudo de alto impacto.

MISSÃO
Criar materiais que realmente aumentem compreensão, retenção, confiança e desempenho escolar do aluno.
O material deve ser útil para estudo real, e não apenas bonito ou genérico.

PERFIL DO ALUNO
Nome: {data['nome']}
Apelido: {data['apelido']}
Idade: {data['idade']}
Série/Ano: {data['serie']}
Escola: {data['escola']}
Turno: {data['turno']}
Responsável: {data['responsavel']}

DIAGNÓSTICOS INFORMADOS
{diags}

PERFIL DE APRENDIZAGEM
{data['perfil_aprendizagem']}

OUTRAS CARACTERÍSTICAS RELEVANTES
{data['outras_caracteristicas'] or 'Não informado'}

INTERESSES DO ALUNO
{data['interesses'] or 'Não informado'}

PRINCÍPIOS OBRIGATÓRIOS
- adaptar linguagem, profundidade e ritmo à idade, série e perfil do aluno
- não gerar material genérico
- não infantilizar excessivamente quando o aluno já suporta mais complexidade
- não resumir demais a ponto de empobrecer o conteúdo
- priorizar clareza, progressão lógica, retenção e aplicação prática
- sempre prever onde o aluno tende a errar
- sempre ajustar a carga textual e o nível de mediação ao perfil de aprendizagem
- considerar o jeito que a escola costuma cobrar
{intensidade_instrucao(data['intensidade'])}
"""

def contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    regras_fontes = (
        "- usar as fontes anexadas para extrair conceitos, vocabulário, exemplos e estilo de cobrança\n"
        "- manter fidelidade conceitual às fontes\n"
        "- não copiar trechos literalmente\n"
        "- não inventar páginas, capítulos ou exercícios específicos se não estiverem explícitos"
        if usa_fontes else
        "- criar material mesmo sem fontes anexadas\n"
        "- usar conhecimento pedagógico compatível com a série\n"
        "- não citar páginas de livro"
    )

    return f"""{build_base_prompt(data)}

CONTEXTO ACADÊMICO
Matéria: {materia}
Conteúdo: {conteudo}
Série/Ano: {data['serie']}
Data da prova: {data['data_prova']}
Dias restantes: {dias}
Situação do conteúdo: {situacao}
Prioridade: {prioridade}
Modo de estudo sugerido: {modo_estudo(dias, situacao)}
Forma de cobrança da escola: {estilo or 'não informada'}
Modo de uso: {'com fontes anexadas' if usa_fontes else 'sem fontes anexadas'}

DECISÕES PEDAGÓGICAS OBRIGATÓRIAS
Antes de gerar o material, considere silenciosamente:
1. Qual o nível de complexidade ideal para esse aluno?
2. Onde ele provavelmente vai errar?
3. O que precisa ser visual, concreto, comparativo ou passo a passo?
4. Quanto texto é adequado sem cansar?
5. Como tornar o material mais memorável?
6. Como alinhar o material ao jeito que a escola cobra?

REGRAS OBRIGATÓRIAS DE QUALIDADE
{regras_fontes}
- não copiar exercícios prontos
- criar exemplos inéditos
- criar explicações progressivas
- usar linguagem natural e didática
- incluir pelo menos 1 estratégia de retenção
- incluir pelo menos 1 estratégia de checagem de compreensão
- destacar pelo menos 1 erro comum previsível
"""

def prompt_video(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """

MATERIAL: ROTEIRO DE VÍDEO DIDÁTICO

OBJETIVO
Criar um roteiro de vídeo curto, altamente claro, envolvente e memorável, com explicação forte o suficiente para realmente melhorar a aprendizagem.

FORMATO OBRIGATÓRIO
1. Objetivo do vídeo em 1 frase
2. Gancho inicial
3. Explicação principal em etapas
4. 3 exemplos progressivos
5. 2 perguntas de interação
6. 1 erro comum + correção
7. 1 mini desafio final
8. 1 frase de fechamento que reforce confiança

REGRAS
- usar linguagem falada, natural e clara
- evitar excesso de abstração
- explicar sem pressa, mas sem enrolar
- trazer imagens mentais, comparações ou analogias quando ajudarem
- adaptar o vocabulário à idade e à matéria
- se for matemática: explicitar raciocínio passo a passo
- se for português ou inglês: destacar padrão, pista, regra e exceção
- se for ciências, história ou geografia: conectar conceito, exemplo e aplicação
- priorizar retenção e compreensão real
"""

def prompt_audio(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """

MATERIAL: ÁUDIO PARA O RESPONSÁVEL

OBJETIVO
Criar um roteiro de áudio curto para orientar o responsável a conduzir o estudo com segurança, sem transformar a explicação em algo técnico demais.

FORMATO OBRIGATÓRIO
1. Objetivo da sessão
2. Como começar
3. Como explicar
4. Onde a criança pode travar
5. Como ajudar sem entregar a resposta
6. Frases prontas para usar
7. Como encerrar e revisar

REGRAS
- falar diretamente com o responsável
- usar linguagem acolhedora, clara e prática
- dar instruções acionáveis
- prever dispersão, ansiedade ou frustração quando pertinente
- orientar mediação adequada ao perfil do aluno
- duração curta e objetiva
"""

def prompt_slides(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """

MATERIAL: SLIDES DE ESTUDO

OBJETIVO
Criar uma sequência de slides realmente útil para estudo, com progressão lógica, clareza e impacto visual-pedagógico.

FORMATO OBRIGATÓRIO
Para cada slide, entregar:
- título do slide
- objetivo do slide
- conteúdo do slide
- sugestão visual
- fala do professor/responsável

ESTRUTURA MÍNIMA
1. Abertura / ativação de conhecimento prévio
2. Conceito principal
3. Explicação guiada
4. Exemplo resolvido ou analisado
5. Erro comum
6. Aplicação prática
7. Desafio curto
8. Fechamento / revisão

REGRAS
- não fazer slides genéricos
- cada slide deve ter função pedagógica clara
- poucas informações por slide, mas com boa densidade
- destacar palavras-chave
- incluir progressão real: entender -> ver modelo -> praticar -> revisar
- adaptar a carga textual ao perfil do aluno
"""

def prompt_flash(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """

MATERIAL: FLASHCARDS DE ALTA RETENÇÃO

OBJETIVO
Criar flashcards para revisão ativa, memorização inteligente e checagem rápida de compreensão.

FORMATO OBRIGATÓRIO
Gerar de 8 a 10 flashcards, cada um com:
- frente
- verso
- tipo do flashcard: conceito / exemplo / comparação / erro comum / aplicação

REGRAS
- variar o tipo de pergunta
- evitar perguntas óbvias demais
- incluir pelo menos:
  - 2 de conceito
  - 2 de aplicação
  - 1 de comparação
  - 1 de erro comum
- respostas curtas, claras e corretas
- nunca ultrapassar 10 flashcards
- priorizar o que mais cai ou mais confunde
"""

def prompt_teste(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """

MATERIAL: TESTE ADAPTADO

OBJETIVO
Criar uma avaliação curta, inteligente e alinhada ao modo como a escola costuma cobrar.

FORMATO OBRIGATÓRIO
1. Objetivo do teste
2. Questões
3. Gabarito comentado
4. Mapa de erros comuns
5. Orientação de correção para o responsável/professor

REGRAS
- criar entre 5 e 8 questões
- misturar níveis: básico, intermediário e desafio leve
- respeitar os formatos de cobrança informados
- variar tipos de questão quando fizer sentido
- não fazer perguntas vagas ou superficiais
- cada questão deve medir uma habilidade clara
- no gabarito, explicar o porquê da resposta
- destacar onde o aluno pode errar e como corrigir
"""

def prompt_aula(data, materia, conteudo, estilo, situacao, prioridade, dias, selected, usa_fontes):
    blocos = [
        contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes),
        """
MATERIAL: PACOTE DE AULA COMPLETA

OBJETIVO
Montar uma sequência pedagógica robusta, coerente e prática, pronta para ser usada em estudo real.

ESTRUTURA OBRIGATÓRIA DA AULA
1. Objetivo principal da aula
2. Habilidade trabalhada
3. Aquecimento / ativação de conhecimento prévio
4. Explicação principal
5. Exemplo guiado
6. Prática orientada
7. Erro comum
8. Checagem de compreensão
9. Fechamento / revisão
10. Orientação breve ao responsável
"""
    ]

    if "Vídeo" in selected:
        blocos.append("""
[VIDEO OVERVIEW]
Gerar um roteiro didático com:
- gancho
- explicação em etapas
- 3 exemplos progressivos
- interação
- erro comum
- mini desafio
""")

    if "Áudio (responsável)" in selected:
        blocos.append("""
[AUDIO OVERVIEW PARA O RESPONSÁVEL]
Gerar um roteiro com:
- como iniciar
- como explicar
- onde a criança pode travar
- frases prontas
- como revisar
""")

    if "Slides" in selected:
        blocos.append("""
[SLIDES]
Organizar uma sequência de slides com:
- título
- objetivo
- conteúdo
- sugestão visual
- fala orientadora
""")

    if "Flashcards (máx 10)" in selected:
        blocos.append("""
[FLASHCARDS]
Gerar entre 8 e 10 flashcards, variados, com foco em revisão ativa, erro comum e aplicação.
""")

    if "Teste" in selected:
        blocos.append("""
[TESTE]
Gerar avaliação curta com:
- 5 a 8 questões
- gabarito comentado
- mapa de erros
- orientação de correção
""")

    blocos.append("""
FECHAMENTO OBRIGATÓRIO
Ao final, incluir:
- 3 sinais de que o aluno realmente entendeu
- 2 sinais de que ainda precisa de reforço
- 1 sugestão de retomada para o dia seguinte
""")

    return "\n".join(blocos)

def prompt_cronograma(data, materia, conteudos, data_hoje, data_prova, alta, media, baixa):
    return f"""{build_base_prompt(data)}

MATERIAL: CRONOGRAMA ESTRATÉGICO ATÉ A PROVA

CONTEXTO
Data de hoje: {data_hoje}
Data da prova: {data_prova}
Matéria: {materia}
Série/Ano: {data['serie']}

CONTEÚDOS DA PROVA
{conteudos}

PRIORIDADES
Alta:
{alta}

Média:
{media}

Baixa:
{baixa}

OBJETIVO
Montar um plano enxuto, realista e eficiente até a prova, respeitando o perfil do aluno e priorizando o que mais impacta o resultado.

FORMATO OBRIGATÓRIO
Para cada dia, informar:
- foco principal
- objetivo do estudo
- duração estimada
- atividade principal
- revisão rápida
- sinal de que o conteúdo foi entendido

REGRAS
- distribuir carga cognitiva sem sobrecarregar
- priorizar conteúdos de maior incidência e maior dificuldade
- alternar novidade e revisão quando fizer sentido
- incluir retomadas espaçadas
- incluir revisão final estratégica no dia anterior
- não detalhar a aula inteira, apenas o plano
"""

def exportar_perfil_json():
    data = get_perfil_data()
    return json.dumps(data, ensure_ascii=False, indent=2)

st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}
.card {
    padding: 18px 20px;
    border-radius: 20px;
    background: white;
    border: 1px solid rgba(15, 23, 42, 0.08);
    box-shadow: 0 8px 26px rgba(15, 23, 42, 0.05);
    margin-bottom: 14px;
}
.small {color: #475569; font-size: 0.92rem;}
h1, h2, h3 {color: #0f172a;}
.section-title {
    font-weight: 700;
    font-size: 1.05rem;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 EduAI Studio - v6")
st.caption("Versão profissional com perfil de aprendizagem refinado, intensidade pedagógica e prompts premium para gerar materiais de estudo mais fortes e úteis.")

tabs = st.tabs([
    "👦 Perfil",
    "🧠 Aprendizagem",
    "🗓️ Cronograma",
    "⚙️ Configuração",
    "🎬 Studio",
    "📦 Aula Completa"
])

with tabs[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Dados principais da criança")
    c1, c2 = st.columns(2)
    st.session_state["nome"] = c1.text_input("Nome", value=st.session_state["nome"])
    st.session_state["apelido"] = c2.text_input("Apelido", value=st.session_state["apelido"])
    st.session_state["idade"] = c1.text_input("Idade", value=st.session_state["idade"])
    st.session_state["serie"] = c2.text_input("Série / Ano", value=st.session_state["serie"])
    st.session_state["escola"] = c1.text_input("Escola", value=st.session_state["escola"])
    st.session_state["turno"] = c2.text_input("Turno", value=st.session_state["turno"])
    st.session_state["interesses"] = st.text_area("Interesses da criança", value=st.session_state["interesses"], height=90)
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
            value=st.session_state["outro_diagnostico"]
        )
    else:
        st.session_state["outro_diagnostico"] = ""

    if (not st.session_state["outras_caracteristicas"].strip()) or st.button("Atualizar características sugeridas"):
        st.session_state["outras_caracteristicas"] = combine_characteristics(
            st.session_state["diagnosticos"],
            st.session_state["outro_diagnostico"]
        )

    st.session_state["outras_caracteristicas"] = st.text_area(
        "Características relevantes (editável)",
        value=st.session_state["outras_caracteristicas"],
        height=120
    )
    st.markdown('<div class="small">Essas informações ajudam a IA a ajustar linguagem, ritmo, mediação e tipo de atividade.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Perfil de aprendizagem refinado")

    a1, a2, a3 = st.columns(3)
    st.session_state["atencao_sustentada"] = a1.selectbox("Atenção sustentada", ATENCAO_OPTIONS, index=ATENCAO_OPTIONS.index(st.session_state["atencao_sustentada"]))
    st.session_state["autonomia"] = a2.selectbox("Autonomia", AUTONOMIA_OPTIONS, index=AUTONOMIA_OPTIONS.index(st.session_state["autonomia"]))
    st.session_state["canal_preferencial"] = a3.selectbox("Canal preferencial", CANAL_OPTIONS, index=CANAL_OPTIONS.index(st.session_state["canal_preferencial"]))

    b1, b2, b3, b4 = st.columns(4)
    st.session_state["tolerancia_frustracao"] = b1.selectbox("Tolerância à frustração", FRUSTRACAO_OPTIONS, index=FRUSTRACAO_OPTIONS.index(st.session_state["tolerancia_frustracao"]))
    st.session_state["leitura_nivel"] = b2.selectbox("Leitura", NIVEL_OPTIONS, index=NIVEL_OPTIONS.index(st.session_state["leitura_nivel"]))
    st.session_state["escrita_nivel"] = b3.selectbox("Escrita", NIVEL_OPTIONS, index=NIVEL_OPTIONS.index(st.session_state["escrita_nivel"]))
    st.session_state["matematica_nivel"] = b4.selectbox("Matemática", NIVEL_OPTIONS, index=NIVEL_OPTIONS.index(st.session_state["matematica_nivel"]))

    c1, c2 = st.columns(2)
    st.session_state["compreensao_oral"] = c1.selectbox("Compreensão oral", ["Baixa", "Média", "Boa"], index=["Baixa", "Média", "Boa"].index(st.session_state["compreensao_oral"]))
    st.session_state["tipo_erro_mais_comum"] = c2.selectbox("Tipo de erro mais comum", ERRO_OPTIONS, index=ERRO_OPTIONS.index(st.session_state["tipo_erro_mais_comum"]))

    st.session_state["engajamento"] = st.text_input("O que mais engaja esse aluno? (ex.: desafio, competição leve, narrativa, exemplos visuais)", value=st.session_state["engajamento"])
    st.session_state["principal_dificuldade"] = st.text_area("Principal dificuldade observada", value=st.session_state["principal_dificuldade"], height=80)
    st.session_state["sinais_quando_trava"] = st.text_area("Sinais quando trava", value=st.session_state["sinais_quando_trava"], height=80)
    st.session_state["melhor_forma_retomar"] = st.text_area("Melhor forma de retomar", value=st.session_state["melhor_forma_retomar"], height=80)

    st.markdown('<div class="small">Essa camada torna o material muito mais adaptado do que usar apenas o nome do diagnóstico.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Plano de estudo até a prova")

    materia_cron = st.text_input("Matéria", key="materia_cron")
    hoje = st.date_input("Data de hoje", value=datetime.date.today(), format="DD/MM/YYYY", key="cron_hoje")
    prova = st.date_input("Data da prova", value=datetime.date.today(), format="DD/MM/YYYY", key="cron_prova")
    conteudos = st.text_area("Conteúdos da prova", height=120, key="conteudos_prova")

    p1, p2, p3 = st.columns(3)
    alta = p1.text_area("Prioridade alta", height=110, key="alta")
    media = p2.text_area("Prioridade média", height=110, key="media")
    baixa = p3.text_area("Prioridade baixa", height=110, key="baixa")

    st.caption(f"Prova marcada para {formatar_data_extenso(prova)}.")

    txt_cron = prompt_cronograma(
        get_perfil_data(formatar_data_br(prova)),
        materia_cron,
        conteudos,
        formatar_data_br(hoje),
        formatar_data_br(prova),
        alta,
        media,
        baixa
    )
    st.text_area("Prompt de cronograma", value=txt_cron, height=340)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[3]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Configuração didática do dia")

    materia = st.text_input("Matéria", key="mat_did")
    conteudo = st.text_input("Conteúdo do dia", key="conteudo_dia")
    hoje2 = st.date_input("Data de hoje", value=datetime.date.today(), format="DD/MM/YYYY", key="did_hoje")
    prova2 = st.date_input("Data da prova", value=datetime.date.today(), format="DD/MM/YYYY", key="did_prova")

    d1, d2, d3 = st.columns(3)
    situacao = d1.selectbox("Situação do conteúdo", SITUACAO_OPTIONS, index=0)
    prioridade = d2.selectbox("Prioridade do conteúdo", PRIORIDADE_OPTIONS, index=0)
    st.session_state["intensidade"] = d3.selectbox("Intensidade pedagógica", INTENSIDADE_OPTIONS, index=INTENSIDADE_OPTIONS.index(st.session_state["intensidade"]))

    st.session_state["usa_fontes"] = st.toggle(
        "Usar com fontes anexadas no NotebookLM",
        value=st.session_state["usa_fontes"]
    )
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
    st.subheader("Resumo do perfil atual para a IA")
    st.text_area("Resumo estruturado", value=exportar_perfil_json(), height=220)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[4]:
    try:
        days = (prova2 - hoje2).days
        estilo = obter_cobranca()
    except Exception:
        days = 0
        materia = ""
        conteudo = ""
        estilo = ""
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
            height=260
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Slides")
        st.text_area(
            "Prompt de slides",
            value=prompt_slides(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=280
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Flashcards")
        st.text_area(
            "Prompt de flashcards",
            value=prompt_flash(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=250
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Áudio do responsável")
        st.text_area(
            "Prompt de áudio",
            value=prompt_audio(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=250
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Teste")
        st.text_area(
            "Prompt de teste",
            value=prompt_teste(perfil, materia, conteudo, estilo, situacao, prioridade, days, usa),
            height=290
        )
        st.markdown('</div>', unsafe_allow_html=True)

with tabs[5]:
    try:
        days = (prova2 - hoje2).days
        estilo = obter_cobranca()
    except Exception:
        days = 0
        materia = ""
        conteudo = ""
        estilo = ""
        situacao = "novo"
        prioridade = "media"
        prova2 = datetime.date.today()

    perfil = get_perfil_data(formatar_data_br(prova2))
    aula = prompt_aula(
        perfil,
        materia,
        conteudo,
        estilo,
        situacao,
        prioridade,
        days,
        st.session_state["selected_materials"],
        st.session_state["usa_fontes"]
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Pacote de aula completa")
    st.text_area("Aula completa", value=aula, height=520)
    st.markdown('</div>', unsafe_allow_html=True)
