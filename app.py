import streamlit as st
import datetime
import json

st.set_page_config(page_title="EduAI Studio", layout="wide")

DIAG_OPTIONS = ["TDAH","TEA nível 1","TEA nível 2","TEA nível 3","Dislexia","Discalculia","Processamento auditivo","Ansiedade","TOD","Outro"]

DIAG_CHARACTERISTICS = {
    "TDAH":["atenção curta","beneficia-se de blocos curtos","precisa de ritmo dinâmico","responde melhor a objetivos claros e rápidos","aprende melhor com estímulos visuais e interação"],
    "TEA nível 1":["beneficia-se de previsibilidade","precisa de instruções claras e objetivas","pode ter dificuldade com linguagem ambígua","responde bem a rotinas estruturadas"],
    "TEA nível 2":["necessita maior estrutura e mediação","precisa de previsibilidade e linguagem muito clara","beneficia-se de passo a passo explícito","pode demandar apoio mais frequente para transições"],
    "TEA nível 3":["necessita alto suporte","precisa de linguagem simples, direta e previsível","beneficia-se de rotinas muito estruturadas","demanda mediação intensiva e apoio constante"],
    "Dislexia":["beneficia-se de menor carga textual","precisa de frases mais curtas","responde melhor a apoio visual","pode cansar com leitura longa"],
    "Discalculia":["precisa de apoio concreto e visual","beneficia-se de progressão muito gradual","responde melhor a exemplos práticos","pode travar diante de abstrações numéricas rápidas"],
    "Processamento auditivo":["beneficia-se de apoio visual constante","pode ter dificuldade com instruções longas faladas","precisa de mensagens curtas e objetivas","responde melhor quando vê e ouve ao mesmo tempo"],
    "Ansiedade":["pode travar sob pressão","precisa de segurança e progressão leve","beneficia-se de previsibilidade e encorajamento objetivo","responde melhor quando o erro é tratado com calma"],
    "TOD":["pode reagir melhor a linguagem neutra e respeitosa","beneficia-se de escolhas simples e combinados claros","responde melhor a estrutura firme sem confronto"],
}

DEFAULT_PROFILE = {
    "nome": "", "apelido": "", "idade": "", "serie": "", "escola": "", "turno": "",
    "interesses": "", "responsavel": "", "diagnosticos": [], "outro_diagnostico": "",
    "outras_caracteristicas": ""
}

def formatar_data_br(data):
    return data.strftime("%d/%m/%Y")

def combine_characteristics(diags, outro_text=""):
    items, seen = [], set()
    for diag in diags:
        if diag == "Outro":
            continue
        for c in DIAG_CHARACTERISTICS.get(diag, []):
            if c not in seen:
                seen.add(c)
                items.append(c)
    if outro_text.strip() and outro_text.strip() not in seen:
        items.append(outro_text.strip())
    return ", ".join(items)

def to_json_bytes(data):
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")

def from_json_file(uploaded_file):
    return json.load(uploaded_file)

def modo_estudo(dias, situacao):
    if dias <= 1:
        return "revisão estratégica"
    if situacao == "novo":
        return "introdução guiada"
    if situacao == "em_dificuldade":
        return "reforço estruturado"
    return "consolidação"

def build_base_prompt(data):
    diag_text = ", ".join(data.get("diagnosticos", [])) if data.get("diagnosticos") else "Nenhum"
    return f'''PROFESSOR PARTICULAR

Você é um professor particular especializado em ensino fundamental, adaptação pedagógica, neuroaprendizagem e personalização de materiais para o perfil da criança abaixo.

PERFIL DA CRIANÇA
Aluno: {data.get("nome","")} ({data.get("apelido","")})
Idade: {data.get("idade","")}
Série: {data.get("serie","")}
Escola: {data.get("escola","")}
Turno: {data.get("turno","")}
Responsável: {data.get("responsavel","")}

DIAGNÓSTICOS INFORMADOS
{diag_text}

OUTRAS CARACTERÍSTICAS RELEVANTES
{data.get("outras_caracteristicas","")}

INTERESSES
{data.get("interesses","")}

REGRAS PEDAGÓGICAS OBRIGATÓRIAS
- adaptar o material ao perfil da criança
- não infantilizar o tom
- usar linguagem clara e respeitosa
- criar exemplos inéditos
- manter progressão: compreensão básica, aplicação e desafio leve
- priorizar apoio visual quando fizer sentido
- evitar excesso de texto e blocos cansativos
'''

def contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    fontes_txt = "com fontes anexadas" if usa_fontes else "sem fontes anexadas"
    regras_fontes = (
        "- usar as fontes anexadas para extrair conceitos, vocabulário e estilo de cobrança\n"
        "- não copiar textos literalmente\n"
        "- não inventar páginas se elas não forem mencionadas"
        if usa_fontes else
        "- criar material mesmo sem fontes anexadas\n"
        "- usar conhecimento pedagógico compatível com a série\n"
        "- não citar páginas de livro"
    )
    return f'''{build_base_prompt(data)}

CONTEXTO
Matéria: {materia}
Conteúdo do dia: {conteudo}
Série: {data.get("serie","")}
Data da prova: {data.get("data_prova","")}
Dias restantes: {dias}
Situação do conteúdo: {situacao}
Prioridade: {prioridade}
Modo de estudo: {modo_estudo(dias, situacao)}
Forma de cobrança da escola:
{estilo or "não informada"}
Modo de uso:
{fontes_txt}

IMPORTANTE
{regras_fontes}
- não copiar exercícios
- criar exemplos inéditos
- adaptar tudo ao perfil da criança
'''

def prompt_video(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + '''
MATERIAL PARA VIDEO OVERVIEW (NotebookLM Studio)

OBJETIVO
Criar um vídeo curto, visual e didático para uma criança.

INSTRUÇÕES
- começar com gancho
- explicar de forma visual e clara
- usar linguagem falada
- incluir 3 exemplos progressivos
- incluir 2 ou 3 momentos de interação
- incluir 1 erro comum
- finalizar com mini desafio
- usar exemplos concretos, adequados à série e ao tema
'''

def prompt_audio_resp(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + '''
MATERIAL PARA AUDIO OVERVIEW (NotebookLM Studio)

OBJETIVO
Criar um áudio para o responsável conduzir a aula.

INSTRUÇÕES
- falar diretamente com o responsável
- explicar objetivo da aula
- orientar como iniciar
- indicar onde a criança pode travar
- orientar como ajudar sem dar resposta
- sugerir frases práticas
- orientar retomada se dispersar
- duração máxima: 5 minutos
- não dar aula para a criança; orientar a condução
'''

def prompt_slides(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + '''
MATERIAL PARA SLIDES (NotebookLM Studio)

OBJETIVO
Criar slides visuais e diretos.

INSTRUÇÕES
- poucos slides
- título curto
- 2 a 4 pontos por slide
- progressão: conceito, exemplo, aplicação, erro comum, desafio
- privilegiar clareza visual
'''

def prompt_flashcards(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + '''
MATERIAL PARA FLASHCARDS (NotebookLM Studio)

OBJETIVO
Criar revisão ativa.

INSTRUÇÕES
- gerar exatamente entre 5 e 10 itens
- limite máximo: 10
- nunca gerar mais de 10
- se começar a exceder 10, interrompa e reduza para 10
- começar fácil, avançar para médio e terminar com desafio leve
- incluir 1 erro comum
- respostas curtas
'''

def prompt_teste(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + '''
MATERIAL PARA TESTE (NotebookLM Studio)

OBJETIVO
Criar avaliação curta.

INSTRUÇÕES
- misturar fácil, médio e desafio leve
- não copiar livro
- incluir gabarito
- destacar erros comuns
- adequar à série e ao tema do dia
'''

def prompt_aula_completa(data, materia, conteudo, estilo, situacao, prioridade, dias, selected, usa_fontes):
    parts = [
        contexto_geral(data, materia, conteudo, estilo, situacao, prioridade, dias, usa_fontes),
        'AULA COMPLETA - PACOTE DE MATERIAIS\n\nOBJETIVO\nCriar todos os materiais solicitados abaixo de forma separada e claramente identificada.'
    ]
    if "Vídeo" in selected:
        parts.append('[VIDEO OVERVIEW]\n- criar roteiro curto, visual e didático\n- incluir gancho, explicação, 3 exemplos progressivos, interação e mini desafio')
    if "Áudio (responsável)" in selected:
        parts.append('[AUDIO OVERVIEW PARA O RESPONSÁVEL]\n- orientar a condução da aula\n- duração máxima: 5 minutos\n- explicar foco, início, possíveis travas, frases úteis e encerramento')
    if "Slides" in selected:
        parts.append('[SLIDES]\n- organizar em poucos slides\n- com títulos curtos, exemplos e erro comum')
    if "Flashcards (máx 10)" in selected:
        parts.append('[FLASHCARDS]\n- gerar entre 5 e 10 itens\n- limite máximo: 10\n- nunca gerar mais de 10')
    if "Teste" in selected:
        parts.append('[TESTE]\n- criar avaliação curta\n- incluir gabarito e erros comuns')
    return "\n\n".join(parts)

def build_cronograma_prompt(data, materia, conteudos, data_hoje, data_prova, prioridade_alta, prioridade_media, prioridade_baixa):
    return f'''{build_base_prompt(data)}

PROMPT - CRONOGRAMA COMPLETO ATE A PROVA

CONTEXTO ATUAL
Data de hoje: {data_hoje}
Data da prova: {data_prova}
Matéria: {materia}
Série: {data.get("serie","")}

CONTEÚDOS DA PROVA
{conteudos}

PRIORIDADE
Alta:
{prioridade_alta}

Média:
{prioridade_media}

Baixa:
{prioridade_baixa}

REGRAS DE PLANEJAMENTO
- dividir o estudo por dias até a prova
- sessões de 15 a 25 minutos
- máximo de 1 conteúdo principal por dia
- priorizar os conteúdos de maior dificuldade e maior chance de cair
- incluir revisão final obrigatória no dia anterior à prova
- não sobrecarregar
- não detalhar a aula
- gerar o plano completo, nunca apenas um dia

FORMATO OBRIGATÓRIO
[DIA X]
Conteúdo do dia:
Duração:
Objetivo:
'''

for k, v in DEFAULT_PROFILE.items():
    st.session_state.setdefault(k, v)
st.session_state.setdefault("usa_fontes", False)
st.session_state.setdefault("selected_materials", ["Vídeo","Áudio (responsável)","Slides"])

st.title("EduAI Studio - v5.6")
st.caption("Com salvar/carregar perfil, modo com/sem fontes e abas Studio/Aula Completa refinadas.")

tabs = st.tabs(["1. Perfil da Criança","2. Cronograma","3. Configuração Didática","4. Studio","5. Aula Completa"])

with tabs[0]:
    st.header("Perfil da Criança")
    c1, c2 = st.columns(2)
    st.session_state["nome"] = c1.text_input("Nome", value=st.session_state["nome"])
    st.session_state["apelido"] = c2.text_input("Apelido", value=st.session_state["apelido"])
    st.session_state["idade"] = c1.text_input("Idade", value=st.session_state["idade"])
    st.session_state["serie"] = c2.text_input("Série / Ano", value=st.session_state["serie"])
    st.session_state["escola"] = c1.text_input("Escola", value=st.session_state["escola"])
    st.session_state["turno"] = c2.text_input("Turno", value=st.session_state["turno"])
    st.session_state["interesses"] = st.text_area("Interesses", value=st.session_state["interesses"], height=100)
    st.session_state["responsavel"] = st.text_input("Nome do responsável", value=st.session_state["responsavel"])

    st.subheader("Diagnósticos")
    st.session_state["diagnosticos"] = st.multiselect("Selecione um ou mais diagnósticos", DIAG_OPTIONS, default=st.session_state["diagnosticos"])

    if "Outro" in st.session_state["diagnosticos"]:
        st.session_state["outro_diagnostico"] = st.text_input("Qual outro diagnóstico?", value=st.session_state["outro_diagnostico"])
    else:
        st.session_state["outro_diagnostico"] = ""

    suggested = combine_characteristics(st.session_state["diagnosticos"], st.session_state["outro_diagnostico"])
    if (not st.session_state["outras_caracteristicas"].strip()) or st.button("Atualizar características sugeridas"):
        st.session_state["outras_caracteristicas"] = suggested

    st.session_state["outras_caracteristicas"] = st.text_area("Outras características (editável)", value=st.session_state["outras_caracteristicas"], height=130)

    perfil_data = {
        "nome": st.session_state["nome"], "apelido": st.session_state["apelido"], "idade": st.session_state["idade"],
        "serie": st.session_state["serie"], "escola": st.session_state["escola"], "turno": st.session_state["turno"],
        "interesses": st.session_state["interesses"], "responsavel": st.session_state["responsavel"],
        "diagnosticos": st.session_state["diagnosticos"] + ([st.session_state["outro_diagnostico"]] if st.session_state["outro_diagnostico"] else []),
        "outras_caracteristicas": st.session_state["outras_caracteristicas"],
    }

    st.text_area("Prompt base gerado automaticamente", value=build_base_prompt(perfil_data), height=280)

    d1, d2 = st.columns(2)
    d1.download_button("Salvar perfil (JSON)", to_json_bytes(perfil_data), file_name="perfil_crianca_v5_6.json")
    up = d2.file_uploader("Carregar perfil (JSON)", type=["json"])
    if up is not None:
        try:
            loaded = from_json_file(up)
            for k in DEFAULT_PROFILE.keys():
                if k in loaded:
                    st.session_state[k] = loaded[k]
            loaded_diags = loaded.get("diagnosticos", [])
            known = [d for d in loaded_diags if d in DIAG_OPTIONS]
            unknown = [d for d in loaded_diags if d not in DIAG_OPTIONS]
            if unknown and "Outro" not in known:
                known.append("Outro")
            st.session_state["diagnosticos"] = known
            st.session_state["outro_diagnostico"] = ", ".join(unknown)
            st.success("Perfil carregado.")
        except Exception as e:
            st.error(f"Erro ao carregar perfil: {e}")

with tabs[1]:
    st.header("Cronograma da Matéria")
    materia_cron = st.text_input("Matéria", key="materia_cron")
    hoje = st.date_input("Data de hoje", value=datetime.date.today(), format="DD/MM/YYYY", key="cron_hoje")
    prova = st.date_input("Data da prova", value=datetime.date.today(), format="DD/MM/YYYY", key="cron_prova")
    conteudos_prova = st.text_area("Conteúdos da prova", key="conteudos_prova", height=120)
    a1, a2, a3 = st.columns(3)
    prioridade_alta = a1.text_area("Prioridade alta", key="prioridade_alta", height=120)
    prioridade_media = a2.text_area("Prioridade média", key="prioridade_media", height=120)
    prioridade_baixa = a3.text_area("Prioridade baixa", key="prioridade_baixa", height=120)

    perfil_data = {
        "nome": st.session_state["nome"], "apelido": st.session_state["apelido"], "idade": st.session_state["idade"],
        "serie": st.session_state["serie"], "escola": st.session_state["escola"], "turno": st.session_state["turno"],
        "interesses": st.session_state["interesses"], "responsavel": st.session_state["responsavel"],
        "diagnosticos": st.session_state["diagnosticos"] + ([st.session_state["outro_diagnostico"]] if st.session_state["outro_diagnostico"] else []),
        "outras_caracteristicas": st.session_state["outras_caracteristicas"],
    }
    cron_prompt = build_cronograma_prompt(perfil_data, materia_cron, conteudos_prova, formatar_data_br(hoje), formatar_data_br(prova), prioridade_alta, prioridade_media, prioridade_baixa)
    st.text_area("Prompt de cronograma", value=cron_prompt, height=320)
    st.download_button("Baixar prompt de cronograma", cron_prompt.encode("utf-8"), file_name="cronograma_v5_6.txt")

with tabs[2]:
    st.header("Configuração Didática")
    materia = st.text_input("Matéria", key="mat_did")
    conteudo = st.text_input("Conteúdo do dia", key="conteudo_dia")
    hoje2 = st.date_input("Data de hoje", value=datetime.date.today(), format="DD/MM/YYYY", key="did_hoje")
    prova2 = st.date_input("Data da prova", value=datetime.date.today(), format="DD/MM/YYYY", key="did_prova")
    estilo = st.text_area("Como a escola cobra", key="estilo_cobranca", height=100)
    situacao = st.selectbox("Situação do conteúdo", ["novo","ja_visto","em_dificuldade"], index=0)
    prioridade = st.selectbox("Prioridade do conteúdo", ["alta","media","baixa"], index=0)
    st.session_state["usa_fontes"] = st.toggle("Usar com fontes anexadas no NotebookLM", value=st.session_state["usa_fontes"])
    st.session_state["selected_materials"] = st.multiselect(
        "Escolha os materiais",
        ["Vídeo","Áudio (responsável)","Slides","Flashcards (máx 10)","Teste"],
        default=st.session_state["selected_materials"]
    )
    days_num = (prova2 - hoje2).days
    st.info(f"Dias até a prova: {days_num} | Modo sugerido: {modo_estudo(days_num, situacao)}")

def get_perfil_data():
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
        "data_prova": formatar_data_br(prova2) if "prova2" in locals() else "",
    }

with tabs[3]:
    st.header("Studio")
    perfil_data = get_perfil_data()
    try:
        days_num = (prova2 - hoje2).days
    except Exception:
        days_num = 0
        materia = conteudo = estilo = ""
        situacao = "novo"
        prioridade = "media"

    use_sources = st.session_state["usa_fontes"]
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Vídeo")
        txt = prompt_video(perfil_data, materia, conteudo, estilo, situacao, prioridade, days_num, use_sources)
        st.text_area("Prompt de vídeo", txt, height=210)
        st.download_button("Baixar vídeo", txt.encode("utf-8"), file_name="video_v5_6.txt")

        st.subheader("Slides")
        txt = prompt_slides(perfil_data, materia, conteudo, estilo, situacao, prioridade, days_num, use_sources)
        st.text_area("Prompt de slides", txt, height=210)
        st.download_button("Baixar slides", txt.encode("utf-8"), file_name="slides_v5_6.txt")

        st.subheader("Flashcards")
        txt = prompt_flashcards(perfil_data, materia, conteudo, estilo, situacao, prioridade, days_num, use_sources)
        st.text_area("Prompt de flashcards", txt, height=210)
        st.download_button("Baixar flashcards", txt.encode("utf-8"), file_name="flashcards_v5_6.txt")

    with c2:
        st.subheader("Áudio do responsável")
        txt = prompt_audio_resp(perfil_data, materia, conteudo, estilo, situacao, prioridade, days_num, use_sources)
        st.text_area("Prompt de áudio", txt, height=210)
        st.download_button("Baixar áudio", txt.encode("utf-8"), file_name="audio_responsavel_v5_6.txt")

        st.subheader("Teste")
        txt = prompt_teste(perfil_data, materia, conteudo, estilo, situacao, prioridade, days_num, use_sources)
        st.text_area("Prompt de teste", txt, height=210)
        st.download_button("Baixar teste", txt.encode("utf-8"), file_name="teste_v5_6.txt")

with tabs[4]:
    st.header("Aula Completa")
    perfil_data = get_perfil_data()
    try:
        days_num = (prova2 - hoje2).days
    except Exception:
        days_num = 0
        materia = conteudo = estilo = ""
        situacao = "novo"
        prioridade = "media"
    aula = prompt_aula_completa(
        perfil_data, materia, conteudo, estilo, situacao, prioridade, days_num,
        st.session_state["selected_materials"], st.session_state["usa_fontes"]
    )
    st.text_area("Pacote de aula completa", aula, height=420)
    st.download_button("Baixar aula completa", aula.encode("utf-8"), file_name="aula_completa_v5_6.txt")
