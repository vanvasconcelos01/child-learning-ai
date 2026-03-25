import streamlit as st
import datetime

st.set_page_config(page_title='EduAI Studio', layout='wide')

DIAG_OPTIONS = ['TDAH','TEA nível 1','TEA nível 2','TEA nível 3','Dislexia','Discalculia','Processamento auditivo','Ansiedade','TOD','Outro']
DIAG_CHARACTERISTICS = {
    'TDAH':['atenção curta','beneficia-se de blocos curtos','precisa de ritmo dinâmico','responde melhor a objetivos claros e rápidos','aprende melhor com estímulos visuais e interação'],
    'TEA nível 1':['beneficia-se de previsibilidade','precisa de instruções claras e objetivas','pode ter dificuldade com linguagem ambígua','responde bem a rotinas estruturadas'],
    'TEA nível 2':['necessita maior estrutura e mediação','precisa de previsibilidade e linguagem muito clara','beneficia-se de passo a passo explícito','pode demandar apoio mais frequente para transições'],
    'TEA nível 3':['necessita alto suporte','precisa de linguagem simples, direta e previsível','beneficia-se de rotinas muito estruturadas','demanda mediação intensiva e apoio constante'],
    'Dislexia':['beneficia-se de menor carga textual','precisa de frases mais curtas','responde melhor a apoio visual','pode cansar com leitura longa'],
    'Discalculia':['precisa de apoio concreto e visual','beneficia-se de progressão muito gradual','responde melhor a exemplos práticos','pode travar diante de abstrações numéricas rápidas'],
    'Processamento auditivo':['beneficia-se de apoio visual constante','pode ter dificuldade com instruções longas faladas','precisa de mensagens curtas e objetivas','responde melhor quando vê e ouve ao mesmo tempo'],
    'Ansiedade':['pode travar sob pressão','precisa de segurança e progressão leve','beneficia-se de previsibilidade e encorajamento objetivo','responde melhor quando o erro é tratado com calma'],
    'TOD':['pode reagir melhor a linguagem neutra e respeitosa','beneficia-se de escolhas simples e combinados claros','responde melhor a estrutura firme sem confronto'],
}
ESCOLA_COBRANCA_OPTIONS = [
    'questões objetivas','questões dissertativas curtas','interpretação de texto','interpretação com imagens',
    'situações do cotidiano','resolução passo a passo','comparação entre conceitos','associação de colunas',
    'verdadeiro ou falso','completar lacunas','sequência lógica / ordenação','mapas, gráficos ou tabelas',
    'vocabulário e definições','produção de resposta oral'
]
PT_MONTHS = {1:'janeiro',2:'fevereiro',3:'março',4:'abril',5:'maio',6:'junho',7:'julho',8:'agosto',9:'setembro',10:'outubro',11:'novembro',12:'dezembro'}

defaults = {'nome':'','apelido':'','idade':'','serie':'','escola':'','turno':'','interesses':'','responsavel':'','diagnosticos':[],'outro_diagnostico':'','outras_caracteristicas':'','usa_fontes':False,'selected_materials':['Vídeo','Áudio (responsável)','Slides'],'cobranca_escola':[],'cobranca_extra':''}
for k,v in defaults.items():
    st.session_state.setdefault(k, v)

def formatar_data_br(d): return d.strftime('%d/%m/%Y')
def formatar_data_pt_extenso(d): return f"{d.day} de {PT_MONTHS[d.month]} de {d.year}"
def modo_estudo(dias, situacao):
    if dias <= 1: return 'revisão estratégica'
    if situacao == 'novo': return 'introdução guiada'
    if situacao == 'em_dificuldade': return 'reforço estruturado'
    return 'consolidação'
def combine_characteristics(diags, outro=''):
    items=[]; seen=set()
    for diag in diags:
        if diag=='Outro': continue
        for c in DIAG_CHARACTERISTICS.get(diag,[]):
            if c not in seen:
                seen.add(c); items.append(c)
    if outro.strip() and outro.strip() not in seen: items.append(outro.strip())
    return ', '.join(items)
def obter_cobranca():
    vals=list(st.session_state['cobranca_escola'])
    if st.session_state['cobranca_extra'].strip(): vals.append(st.session_state['cobranca_extra'].strip())
    return ', '.join(vals)
def get_perfil(data_prova=''):
    return {
        'nome':st.session_state['nome'],'apelido':st.session_state['apelido'],'idade':st.session_state['idade'],
        'serie':st.session_state['serie'],'escola':st.session_state['escola'],'turno':st.session_state['turno'],
        'interesses':st.session_state['interesses'],'responsavel':st.session_state['responsavel'],
        'diagnosticos':st.session_state['diagnosticos'] + ([st.session_state['outro_diagnostico']] if st.session_state['outro_diagnostico'] else []),
        'outras_caracteristicas':st.session_state['outras_caracteristicas'],'data_prova':data_prova
    }
def build_base_prompt(data):
    diags=', '.join(data['diagnosticos']) if data['diagnosticos'] else 'Nenhum'
    return f'''PROFESSOR PARTICULAR

Você é um professor particular especializado em ensino fundamental, adaptação pedagógica, neuroaprendizagem e personalização de materiais para o perfil da criança abaixo.

PERFIL DA CRIANÇA
Aluno: {data['nome']} ({data['apelido']})
Idade: {data['idade']}
Série: {data['serie']}
Escola: {data['escola']}
Turno: {data['turno']}
Responsável: {data['responsavel']}

DIAGNÓSTICOS INFORMADOS
{diags}

OUTRAS CARACTERÍSTICAS RELEVANTES
{data['outras_caracteristicas']}

INTERESSES
{data['interesses']}
'''
def contexto_geral(data,materia,conteudo,estilo,situacao,prioridade,dias,usa_fontes):
    regras = ('- usar as fontes anexadas para extrair conceitos, vocabulário e estilo de cobrança\n- não copiar textos literalmente\n- não inventar páginas se elas não forem mencionadas'
              if usa_fontes else
              '- criar material mesmo sem fontes anexadas\n- usar conhecimento pedagógico compatível com a série\n- não citar páginas de livro')
    return f'''{build_base_prompt(data)}
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
- adaptar tudo ao perfil da criança
'''
def prompt_video(data,materia,conteudo,estilo,situacao,prioridade,dias,usa_fontes):
    return contexto_geral(data,materia,conteudo,estilo,situacao,prioridade,dias,usa_fontes)+'''MATERIAL PARA VIDEO OVERVIEW (NotebookLM Studio)

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
'''
def prompt_audio(data,materia,conteudo,estilo,situacao,prioridade,dias,usa_fontes):
    return contexto_geral(data,materia,conteudo,estilo,situacao,prioridade,dias,usa_fontes)+'''MATERIAL PARA AUDIO OVERVIEW (NotebookLM Studio)

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
'''
def prompt_slides(data,materia,conteudo,estilo,situacao,prioridade,dias,usa_fontes):
    return contexto_geral(data,materia,conteudo,estilo,situacao,prioridade,dias,usa_fontes)+'''MATERIAL PARA SLIDES (NotebookLM Studio)

OBJETIVO
Criar slides visuais e diretos.

INSTRUÇÕES
- poucos slides
- título curto
- 2 a 4 pontos por slide
- progressão: conceito, exemplo, aplicação, erro comum, desafio
'''
def prompt_flash(data,materia,conteudo,estilo,situacao,prioridade,dias,usa_fontes):
    return contexto_geral(data,materia,conteudo,estilo,situacao,prioridade,dias,usa_fontes)+'''MATERIAL PARA FLASHCARDS (NotebookLM Studio)

OBJETIVO
Criar revisão ativa.

INSTRUÇÕES
- gerar exatamente entre 5 e 10 itens
- limite máximo: 10
- nunca gerar mais de 10
- se começar a exceder 10, interrompa e reduza para 10
- incluir 1 erro comum
'''
def prompt_teste(data,materia,conteudo,estilo,situacao,prioridade,dias,usa_fontes):
    return contexto_geral(data,materia,conteudo,estilo,situacao,prioridade,dias,usa_fontes)+'''MATERIAL PARA TESTE (NotebookLM Studio)

OBJETIVO
Criar avaliação curta.

INSTRUÇÕES
- misturar fácil, médio e desafio leve
- incluir gabarito
- destacar erros comuns
'''
def prompt_aula(data,materia,conteudo,estilo,situacao,prioridade,dias,selected,usa_fontes):
    parts=[contexto_geral(data,materia,conteudo,estilo,situacao,prioridade,dias,usa_fontes),'AULA COMPLETA - PACOTE DE MATERIAIS']
    if 'Vídeo' in selected: parts.append('[VIDEO OVERVIEW]\n- criar roteiro curto, visual e didático')
    if 'Áudio (responsável)' in selected: parts.append('[AUDIO OVERVIEW PARA O RESPONSÁVEL]\n- orientar a condução da aula')
    if 'Slides' in selected: parts.append('[SLIDES]\n- organizar em poucos slides')
    if 'Flashcards (máx 10)' in selected: parts.append('[FLASHCARDS]\n- gerar entre 5 e 10 itens, máximo 10')
    if 'Teste' in selected: parts.append('[TESTE]\n- criar avaliação curta com gabarito')
    return '\n\n'.join(parts)
def prompt_cronograma(data,materia,conteudos,data_hoje,data_prova,alta,media,baixa):
    return f'''{build_base_prompt(data)}
PROMPT - CRONOGRAMA COMPLETO ATE A PROVA

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

FORMATO OBRIGATÓRIO
[DIA X]
Conteúdo do dia:
Duração:
Objetivo:
'''

st.title('EduAI Studio - v5.7')
st.caption('Perfil salvo na própria página, datas em pt-BR nos resumos e formas de cobrança por seleção.')

tabs = st.tabs(['1. Perfil da Criança','2. Cronograma','3. Configuração Didática','4. Studio','5. Aula Completa'])

with tabs[0]:
    st.header('Perfil da Criança')
    c1,c2=st.columns(2)
    st.session_state['nome']=c1.text_input('Nome', value=st.session_state['nome'])
    st.session_state['apelido']=c2.text_input('Apelido', value=st.session_state['apelido'])
    st.session_state['idade']=c1.text_input('Idade', value=st.session_state['idade'])
    st.session_state['serie']=c2.text_input('Série / Ano', value=st.session_state['serie'])
    st.session_state['escola']=c1.text_input('Escola', value=st.session_state['escola'])
    st.session_state['turno']=c2.text_input('Turno', value=st.session_state['turno'])
    st.session_state['interesses']=st.text_area('Interesses', value=st.session_state['interesses'], height=100)
    st.session_state['responsavel']=st.text_input('Nome do responsável', value=st.session_state['responsavel'])
    st.subheader('Diagnósticos')
    st.session_state['diagnosticos']=st.multiselect('Selecione um ou mais diagnósticos', DIAG_OPTIONS, default=st.session_state['diagnosticos'])
    if 'Outro' in st.session_state['diagnosticos']:
        st.session_state['outro_diagnostico']=st.text_input('Qual outro diagnóstico?', value=st.session_state['outro_diagnostico'])
    else:
        st.session_state['outro_diagnostico']=''
    if (not st.session_state['outras_caracteristicas'].strip()) or st.button('Atualizar características sugeridas'):
        st.session_state['outras_caracteristicas']=combine_characteristics(st.session_state['diagnosticos'], st.session_state['outro_diagnostico'])
    st.session_state['outras_caracteristicas']=st.text_area('Outras características (editável)', value=st.session_state['outras_caracteristicas'], height=130)
    st.success('O perfil fica salvo na própria página enquanto você usa este app.')
    st.text_area('Prompt base gerado automaticamente', value=build_base_prompt(get_perfil_data()), height=240)

with tabs[1]:
    st.header('Cronograma da Matéria')
    materia_cron=st.text_input('Matéria', key='materia_cron')
    hoje=st.date_input('Data de hoje', value=datetime.date.today(), format='DD/MM/YYYY', key='cron_hoje')
    prova=st.date_input('Data da prova', value=datetime.date.today(), format='DD/MM/YYYY', key='cron_prova')
    conteudos=st.text_area('Conteúdos da prova', height=120, key='conteudos_prova')
    a1,a2,a3=st.columns(3)
    alta=a1.text_area('Prioridade alta', height=120, key='alta')
    media=a2.text_area('Prioridade média', height=120, key='media')
    baixa=a3.text_area('Prioridade baixa', height=120, key='baixa')
    st.caption(f'Prova marcada para {formatar_data_pt_extenso(prova)}.')
    txt=prompt_cronograma(get_perfil_data(), materia_cron, conteudos, formatar_data_br(hoje), formatar_data_br(prova), alta, media, baixa)
    st.text_area('Prompt de cronograma', value=txt, height=300)

with tabs[2]:
    st.header('Configuração Didática')
    materia=st.text_input('Matéria', key='mat_did')
    conteudo=st.text_input('Conteúdo do dia', key='conteudo_dia')
    hoje2=st.date_input('Data de hoje', value=datetime.date.today(), format='DD/MM/YYYY', key='did_hoje')
    prova2=st.date_input('Data da prova', value=datetime.date.today(), format='DD/MM/YYYY', key='did_prova')
    situacao=st.selectbox('Situação do conteúdo', ['novo','ja_visto','em_dificuldade'], index=0)
    prioridade=st.selectbox('Prioridade do conteúdo', ['alta','media','baixa'], index=0)
    st.session_state['usa_fontes']=st.toggle('Usar com fontes anexadas no NotebookLM', value=st.session_state['usa_fontes'])
    st.subheader('Como a escola cobra')
    st.session_state['cobranca_escola']=st.multiselect('Selecione os tipos de cobrança mais comuns', ESCOLA_COBRANCA_OPTIONS, default=st.session_state['cobranca_escola'])
    st.session_state['cobranca_extra']=st.text_input('Outro tipo de cobrança (opcional)', value=st.session_state['cobranca_extra'])
    st.subheader('Materiais')
    st.session_state['selected_materials']=st.multiselect('Escolha os materiais', ['Vídeo','Áudio (responsável)','Slides','Flashcards (máx 10)','Teste'], default=st.session_state['selected_materials'])
    st.info(f'Dias até a prova: {(prova2-hoje2).days} | Modo sugerido: {modo_estudo((prova2-hoje2).days, situacao)}')
    st.caption(f'Prova marcada para {formatar_data_pt_extenso(prova2)}.')

with tabs[3]:
    st.header('Studio')
    try:
        days=(prova2-hoje2).days
        estilo=obter_cobranca()
    except Exception:
        days=0; materia=''; conteudo=''; estilo=''; situacao='novo'; prioridade='media'; prova2=datetime.date.today()
    perfil=get_perfil_data(formatar_data_br(prova2))
    usa=st.session_state['usa_fontes']
    c1,c2=st.columns(2)
    with c1:
        st.subheader('Vídeo')
        st.text_area('Prompt de vídeo', value=prompt_video(perfil,materia,conteudo,estilo,situacao,prioridade,days,usa), height=200)
        st.subheader('Slides')
        st.text_area('Prompt de slides', value=prompt_slides(perfil,materia,conteudo,estilo,situacao,prioridade,days,usa), height=200)
        st.subheader('Flashcards')
        st.text_area('Prompt de flashcards', value=prompt_flash(perfil,materia,conteudo,estilo,situacao,prioridade,days,usa), height=200)
    with c2:
        st.subheader('Áudio do responsável')
        st.text_area('Prompt de áudio', value=prompt_audio(perfil,materia,conteudo,estilo,situacao,prioridade,days,usa), height=200)
        st.subheader('Teste')
        st.text_area('Prompt de teste', value=prompt_teste(perfil,materia,conteudo,estilo,situacao,prioridade,days,usa), height=200)

with tabs[4]:
    st.header('Aula Completa')
    try:
        days=(prova2-hoje2).days
        estilo=obter_cobranca()
    except Exception:
        days=0; materia=''; conteudo=''; estilo=''; situacao='novo'; prioridade='media'; prova2=datetime.date.today()
    perfil=get_perfil_data(formatar_data_br(prova2))
    aula=prompt_aula(perfil,materia,conteudo,estilo,situacao,prioridade,days,st.session_state['selected_materials'],st.session_state['usa_fontes'])
    st.text_area('Pacote de aula completa', value=aula, height=380)
