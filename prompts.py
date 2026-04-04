import streamlit as st
from profile_logic import resumo_aluno_compacto, modo_estudo

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
