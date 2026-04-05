import streamlit as st
from profile_logic import resumo_aluno_compacto, modo_estudo

def get_subject_specialization(materia: str, area: str = "") -> str:
    area_norm = (area or "").strip().lower()
    m = (materia or "").strip().lower()

    if area_norm == "linguagens":
        return (
            "Assuma postura de especialista em Linguagens, com foco em leitura, interpretação, "
            "produção textual, análise de linguagem, comunicação, repertório e adaptação à idade do aluno."
        )

    if area_norm == "exatas":
        return (
            "Assuma postura de especialista em Exatas, com foco em raciocínio lógico, progressão passo a passo, "
            "clareza conceitual, resolução estruturada e adaptação à idade e às dificuldades do aluno."
        )

    if area_norm == "ciências da natureza":
        return (
            "Assuma postura de especialista em Ciências da Natureza, com foco em investigação, observação, "
            "fenômenos, relações entre teoria e prática, linguagem acessível e clareza visual."
        )

    if area_norm == "humanas":
        return (
            "Assuma postura de especialista em Ciências Humanas, com foco em contexto, comparação, "
            "causa e consequência, leitura crítica, interpretação e adaptação à idade do aluno."
        )

    if area_norm == "idiomas":
        return (
            "Assuma postura de especialista em ensino de idiomas para aluno brasileiro. "
            "Explique utilizando também o português do Brasil para apoiar a compreensão. "
            "Mesmo em vídeo e slides, não deixe o material apenas no idioma estudado."
        )

    if area_norm == "artes":
        return (
            "Assuma postura de especialista em Artes, com foco em expressão, leitura de imagem, "
            "elementos visuais, contexto cultural, criatividade e apreciação estética."
        )

    if area_norm == "tecnologia":
        return (
            "Assuma postura de especialista em tecnologia educacional e informática, "
            "com foco em lógica, uso prático, linguagem acessível e resolução passo a passo."
        )

    if any(x in m for x in ["portugu", "reda", "gram", "liter", "produção textual", "producao textual"]):
        return (
            "Assuma postura de especialista em pedagogia da Língua Portuguesa, "
            "alfabetização, leitura, interpretação de texto, produção textual, gramática contextualizada, "
            "ortografia e desenvolvimento da linguagem, sempre adaptando à idade e às dificuldades do aluno."
        )

    if any(x in m for x in ["mat", "geometr", "aritm", "álgebra", "algebra"]):
        return (
            "Assuma postura de especialista em Matemática e ensino de exatas, "
            "com foco em raciocínio lógico, progressão passo a passo, uso de exemplos concretos, "
            "clareza conceitual e adaptação à idade e às dificuldades do aluno."
        )

    if any(x in m for x in ["ingl", "english", "espanhol", "idioma", "língua estrangeira", "lingua estrangeira", "francês", "frances"]):
        return (
            "Assuma postura de especialista em ensino de idiomas para aluno brasileiro. "
            "Explique utilizando também o português do Brasil para apoiar a compreensão. "
            "Mesmo em vídeo e slides, não deixe o material apenas no idioma estudado; "
            "use explicações, apoio e contextualização em português do Brasil."
        )

    if "hist" in m:
        return (
            "Assuma postura de especialista em História, com foco em linha do tempo, "
            "contexto histórico, causa e consequência, comparação entre períodos, leitura crítica "
            "de acontecimentos e adaptação à idade do aluno."
        )

    if "geogr" in m:
        return (
            "Assuma postura de especialista em Geografia, com foco em espaço geográfico, mapas, território, "
            "paisagem, clima, população, economia, relações sociedade-natureza e leitura de mapas e gráficos."
        )

    if "ciên" in m or "cien" in m:
        return (
            "Assuma postura de especialista em Ciências, com foco em investigação, observação, experimentação, "
            "corpo humano, meio ambiente, matéria, energia e explicação acessível de fenômenos."
        )

    if "biolog" in m:
        return (
            "Assuma postura de especialista em Biologia, com foco em seres vivos, corpo humano, ecologia, genética, "
            "evolução e relações entre estrutura e função, sempre com clareza visual e linguagem acessível."
        )

    if "fís" in m or "fis" in m:
        return (
            "Assuma postura de especialista em Física, com foco em fenômenos físicos, movimento, força, energia, "
            "interpretação de situações-problema e explicação progressiva do conceito ao cálculo."
        )

    if "quím" in m or "quim" in m:
        return (
            "Assuma postura de especialista em Química, com foco em substâncias, misturas, transformações da matéria, "
            "reações químicas, linguagem simbólica e associação entre teoria e exemplos concretos."
        )

    if "arte" in m:
        return (
            "Assuma postura de especialista em Artes, com foco em leitura de imagem, expressão artística, "
            "elementos visuais, contexto cultural, produção criativa e apreciação estética, adaptando à idade do aluno."
        )

    if "filos" in m:
        return (
            "Assuma postura de especialista em Filosofia, com foco em pensamento crítico, conceitos centrais, "
            "interpretação de ideias, argumentação e simplificação didática sem perder profundidade."
        )

    if "sociolog" in m:
        return (
            "Assuma postura de especialista em Sociologia, com foco em sociedade, cultura, cidadania, "
            "grupos sociais, desigualdade, comportamento coletivo e leitura crítica do cotidiano."
        )

    if "relig" in m:
        return (
            "Assuma postura de especialista em Ensino Religioso, com foco em valores, diversidade, "
            "tradições, convivência, respeito e compreensão contextualizada, sempre adequada à idade do aluno."
        )

    if any(x in m for x in ["inform", "tecnolog", "comput", "program", "robótica", "robotica"]):
        return (
            "Assuma postura de especialista em tecnologia educacional e informática, "
            "com foco em lógica, uso prático, linguagem acessível, resolução passo a passo e adaptação ao nível do aluno."
        )

    return (
        "Assuma postura de especialista pedagógico na matéria estudada, "
        "adaptando explicações, exemplos, linguagem e dificuldade à idade e ao perfil do aluno."
    )

def get_language_support_instruction(materia: str, area: str = "") -> str:
    area_norm = (area or "").strip().lower()
    m = (materia or "").strip().lower()

    if area_norm == "idiomas" or any(
        x in m for x in ["ingl", "english", "espanhol", "idioma", "língua estrangeira", "lingua estrangeira", "francês", "frances"]
    ):
        return (
            "IMPORTANTE DE IDIOMA:\n"
            "- usar o idioma estudado com apoio em português do Brasil\n"
            "- explicar vocabulário, estruturas e exemplos em português do Brasil também\n"
            "- vídeo e slides não devem ficar apenas no idioma da matéria"
        )
    return ""

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

def contexto_geral(data, materia, area, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    regras = (
        "- usar as fontes anexadas como base principal\n"
        "- não copiar literalmente\n"
        "- não inventar páginas"
        if usa_fontes else
        "- criar mesmo sem fontes anexadas\n"
        "- usar nível compatível com a série\n"
        "- não citar páginas"
    )

    especialidade = get_subject_specialization(materia, area)
    idioma = get_language_support_instruction(materia, area)

    return f"""{build_base_prompt(data)}
ESPECIALIZAÇÃO PEDAGÓGICA DA MATÉRIA
{especialidade}

CONTEXTO
Matéria: {materia}
Área da matéria: {area or 'não informada'}
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
{idioma}
"""

def contexto_studio_compacto(data, materia, area, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    modo_fontes = "usar as fontes anexadas como base principal" if usa_fontes else "criar sem depender de fontes anexadas"
    objetivo_dia = st.session_state.get("objetivo_dia", "").strip() or "não informado"
    especialidade = get_subject_specialization(materia, area)
    idioma = get_language_support_instruction(materia, area)

    return f"""CRIE O MATERIAL FINAL PARA O NOTEBOOKLM STUDIO.

ESPECIALIZAÇÃO PEDAGÓGICA DA MATÉRIA
{especialidade}

CONTEXTO DO ESTUDO
- Matéria: {materia or 'não informada'}
- Área da matéria: {area or 'não informada'}
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
{idioma}
"""

def prompt_video(data, materia, area, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, area, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """
Crie o VIDEO OVERVIEW final, pronto para uso.
Explique o conteúdo de forma clara, envolvente e adaptada ao aluno.
Inclua exemplos alinhados ao perfil e interesses do aluno, trate o erro comum esperado e finalize com revisão breve.
Saída final pronta para o Studio.
"""

def prompt_audio(data, materia, area, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, area, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """
Crie o AUDIO OVERVIEW final, pronto para uso pelo responsável.
Explique como conduzir esse conteúdo com esse aluno, onde ele pode travar, como retomar e como revisar.
Use linguagem natural, prática e acolhedora.
Saída final pronta para o Studio.
"""

def prompt_slides(data, materia, area, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, area, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """
Crie os SLIDES finais do estudo.
Organize com progressão clara: conceito, exemplo, erro comum, aplicação e revisão.
Use pouco texto por slide e linguagem adequada ao aluno.
Saída final pronta para o Studio.
"""

def prompt_flash(data, materia, area, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, area, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """
Crie os FLASHCARDS finais.
Gere de 6 a 8 flashcards úteis para esse aluno, com foco em conceito, aplicação, comparação e erro comum.
Saída final pronta para o Studio.
"""

def prompt_teste(data, materia, area, conteudo, estilo, situacao, prioridade, dias, usa_fontes):
    return contexto_studio_compacto(data, materia, area, conteudo, estilo, situacao, prioridade, dias, usa_fontes) + """
Crie o TESTE final.
Gere 5 questões adaptadas ao aluno e ao formato de cobrança da escola, com gabarito comentado e erros comuns esperados.
Saída final pronta para o Studio.
"""

def prompt_aula(data, materia, area, conteudo, estilo, situacao, prioridade, dias, selected, usa_fontes):
    parts = [
        contexto_geral(data, materia, area, conteudo, estilo, situacao, prioridade, dias, usa_fontes),
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

def prompt_cronograma(data, materia, area, conteudos, data_hoje, data_prova, alta, media, baixa):
    especialidade = get_subject_specialization(materia, area)
    idioma = get_language_support_instruction(materia, area)

    return f"""{build_base_prompt(data)}
ESPECIALIZAÇÃO PEDAGÓGICA DA MATÉRIA
{especialidade}

CRONOGRAMA ATÉ A PROVA

Data de hoje: {data_hoje}
Data da prova: {data_prova}
Matéria: {materia}
Área da matéria: {area or 'não informada'}

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
- o ÚLTIMO DIA ANTES DA PROVA deve ser obrigatoriamente uma REVISÃO GERAL
- o campo TEXTO PARA COLAR EM "CONTEÚDO DO DIA" deve sair pronto para usar na aba Configuração
{idioma}
"""
