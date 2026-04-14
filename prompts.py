def get_subject_specialization(materia: str, area: str = "") -> str:
    area_norm = (area or "").strip().lower()
    m = (materia or "").strip().lower()

    if area_norm == "linguagens":
        return "Especialista em Linguagens, leitura, interpretação, produção textual e adaptação por idade."
    if area_norm == "exatas":
        return "Especialista em Exatas, raciocínio lógico, passo a passo e clareza conceitual."
    if area_norm == "ciências da natureza":
        return "Especialista em Ciências da Natureza, investigação, fenômenos e linguagem acessível."
    if area_norm == "humanas":
        return "Especialista em Ciências Humanas, contexto, comparação, causa e consequência."
    if area_norm == "idiomas":
        return "Especialista em ensino de idiomas para aluno brasileiro, explicando principalmente em português do Brasil."
    if area_norm == "artes":
        return "Especialista em Artes, expressão, leitura de imagem e contexto cultural."
    if area_norm == "tecnologia":
        return "Especialista em tecnologia educacional, lógica, uso prático e explicação passo a passo."

    if any(x in m for x in ["portugu", "reda", "gram", "liter", "produção textual", "producao textual"]):
        return "Especialista em Língua Portuguesa, leitura, interpretação, gramática contextualizada e produção textual."
    if any(x in m for x in ["mat", "geometr", "aritm", "álgebra", "algebra"]):
        return "Especialista em Matemática, raciocínio lógico, exemplos concretos e resolução passo a passo."
    if any(x in m for x in ["ingl", "english", "espanhol", "idioma", "língua estrangeira", "lingua estrangeira", "francês", "frances"]):
        return "Especialista em ensino de idiomas para aluno brasileiro, com explicação principal em português do Brasil."
    if "hist" in m:
        return "Especialista em História, linha do tempo, contexto histórico e leitura crítica."
    if "geogr" in m:
        return "Especialista em Geografia, espaço geográfico, território, paisagem, mapas e gráficos."
    if "ciên" in m or "cien" in m:
        return "Especialista em Ciências, observação, experimentação, corpo humano, meio ambiente, matéria e energia."
    if "biolog" in m:
        return "Especialista em Biologia, seres vivos, ecologia, genética e relações entre estrutura e função."
    if "fís" in m or "fis" in m:
        return "Especialista em Física, fenômenos, movimento, força, energia e interpretação de situações-problema."
    if "quím" in m or "quim" in m:
        return "Especialista em Química, substâncias, misturas, transformações da matéria e reações químicas."
    if "arte" in m:
        return "Especialista em Artes, leitura de imagem, expressão artística e elementos visuais."
    if "filos" in m:
        return "Especialista em Filosofia, pensamento crítico, conceitos centrais e argumentação."
    if "sociolog" in m:
        return "Especialista em Sociologia, sociedade, cultura, cidadania e leitura crítica do cotidiano."
    if "relig" in m:
        return "Especialista em Ensino Religioso, valores, diversidade, convivência e respeito."
    if any(x in m for x in ["inform", "tecnolog", "comput", "program", "robótica", "robotica"]):
        return "Especialista em tecnologia educacional e informática, lógica e resolução passo a passo."

    return "Especialista pedagógico na matéria estudada, adaptando linguagem e dificuldade à idade e ao perfil do aluno."


def get_language_support_instruction(materia: str, area: str = "") -> str:
    area_norm = (area or "").strip().lower()
    m = (materia or "").strip().lower()

    if area_norm == "idiomas" or any(
        x in m for x in ["ingl", "english", "espanhol", "idioma", "língua estrangeira", "lingua estrangeira", "francês", "frances"]
    ):
        return (
            "IDIOMA:\n"
            "- usar português do Brasil como idioma principal de explicação\n"
            "- o idioma estrangeiro deve aparecer como objeto de estudo, prática e vocabulário\n"
            "- vídeo e slides não devem ficar predominantemente no idioma estrangeiro"
        )
    return ""


def build_base_prompt(data):
    diags = ", ".join(data["diagnosticos"]) if data["diagnosticos"] else "Nenhum"
    return f"""PERFIL DO ALUNO
Aluno: {data['nome']} ({data['apelido']})
Idade: {data['idade']}
Série: {data['serie']}
Escola: {data['escola']}
Turno: {data['turno']}
Responsável: {data['responsavel']}

Diagnósticos: {diags}
Características sugeridas: {data.get('caracteristicas_sugeridas', 'não informado') or 'não informado'}
Perfil de aprendizagem:
{data['perfil_aprendizagem']}
Outras características: {data['outras_caracteristicas'] or 'não informado'}
Interesses: {data['interesses'] or 'não informado'}
"""


def contexto_studio_compacto(data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn):
    especialidade = get_subject_specialization(materia, area)
    idioma = get_language_support_instruction(materia, area)
    anexos = "usar anexos só como embasamento; material final autossuficiente" if usa_fontes else "criar sem anexos; material final autossuficiente"

    return f"""Crie material final para NotebookLM Studio.

MATÉRIA: {materia or 'não informada'}
ÁREA: {area or 'não informada'}
CONTEÚDO DO DIA: {conteudo or 'não informado'}
OBJETIVO DO DIA: {objetivo or 'não informado'}
DIAS ATÉ A PROVA: {dias}
SITUAÇÃO: {situacao}
PRIORIDADE: {prioridade}
COMO A ESCOLA COBRA: {estilo or 'não informado'}
ANEXOS: {anexos}

ESPECIALIDADE:
{especialidade}

ALUNO:
{resumo_aluno_fn(data)}

REGRAS:
- usar somente o conteúdo do dia
- alinhar ao que costuma ser mais cobrado para a idade/série dentro do repertório dado
- material totalmente autossuficiente
- não depender de página, imagem, capítulo, trecho ou tela do livro
- não escrever "observe a página", "veja a imagem", "como mostrado acima"
- preservar termos oficiais do conteúdo
- não inventar nomes novos para conceitos, categorias ou classificações
- linguagem clara, útil e direta
{idioma}
"""


def prompt_video(data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn):
    return contexto_studio_compacto(
        data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn
    ) + """
TAREFA: gerar VIDEO OVERVIEW final.

EXIGÊNCIAS:
- vídeo curto
- explicar apenas o conteúdo do dia
- usar exemplos próprios, sem usar página ou imagem do livro
- manter os termos oficiais do conteúdo
- não inventar termos substitutos
- quando fizer pergunta, fazer pausa breve de alguns segundos antes de continuar
- fechar com mini revisão
"""


def prompt_audio(data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn):
    return contexto_studio_compacto(
        data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn
    ) + """
TAREFA: gerar AUDIO OVERVIEW final para o responsável.

EXIGÊNCIAS:
- áudio curto e objetivo
- foco apenas no conteúdo do dia
- resumir o que deve ser estudado hoje
- explicar como conduzir a atividade
- apontar onde o aluno pode travar
- indicar como retomar rapidamente
- manter os termos oficiais do conteúdo
- não inventar termos substitutos
- duração esperada curta, cerca de 2 a 4 minutos
"""


def prompt_slides(data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn):
    return contexto_studio_compacto(
        data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn
    ) + """
TAREFA: gerar SLIDES finais.

EXIGÊNCIAS:
- usar apenas o conteúdo do dia
- progressão: conceito, exemplo, erro comum, aplicação, revisão
- exemplos próprios
- sem telas do livro
- preservar os termos oficiais do conteúdo
- pouco texto por slide
"""


def prompt_flash(data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn):
    return contexto_studio_compacto(
        data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn
    ) + """
TAREFA: gerar FLASHCARDS finais.

EXIGÊNCIAS:
- no máximo 10 cards
- apenas conteúdo do dia
- focar no mais importante, mais cobrado e mais sujeito a erro
- preservar os termos oficiais do conteúdo
"""


def prompt_teste(data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn):
    return contexto_studio_compacto(
        data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn
    ) + """
TAREFA: gerar TESTE final.

EXIGÊNCIAS:
- usar apenas o conteúdo do dia
- gerar 5 questões
- adaptar ao formato de cobrança da escola
- incluir gabarito comentado
- preservar termos oficiais do conteúdo
"""


def prompt_aula(data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, selected, usa_fontes, modo_estudo_fn):
    base = f"""AULA COMPLETA

MATÉRIA: {materia}
ÁREA: {area or 'não informada'}
CONTEÚDO DO DIA: {conteudo}
OBJETIVO DO DIA: {objetivo or 'não informado'}
DIAS ATÉ A PROVA: {dias}
SITUAÇÃO: {situacao}
PRIORIDADE: {prioridade}
MODO DE ESTUDO: {modo_estudo_fn(dias, situacao)}
COMO A ESCOLA COBRA: {estilo or 'não informado'}

REGRAS:
- usar só o conteúdo do dia
- preservar termos oficiais
- não inventar conceitos
- material autossuficiente
"""

    parts = [base]

    if "Vídeo" in selected:
        parts.append("[VIDEO OVERVIEW]\n- vídeo curto, com exemplos próprios e pausas após perguntas")
    if "Áudio (responsável)" in selected:
        parts.append("[AUDIO OVERVIEW]\n- áudio curto, direto e objetivo para condução do estudo do dia")
    if "Slides" in selected:
        parts.append("[SLIDES]\n- slides autossuficientes, sem depender do livro")
    if "Flashcards (máx 10)" in selected:
        parts.append("[FLASHCARDS]\n- no máximo 10 cards, apenas do conteúdo do dia")
    if "Teste" in selected:
        parts.append("[TESTE]\n- 5 questões com gabarito")

    return "\n\n".join(parts)


def prompt_cronograma(data, materia, area, conteudos, data_hoje, data_prova, alta, media, baixa):
    especialidade = get_subject_specialization(materia, area)
    idioma = get_language_support_instruction(materia, area)

    return f"""{build_base_prompt(data)}
ESPECIALIDADE:
{especialidade}

CRONOGRAMA ATÉ A PROVA

Hoje: {data_hoje}
Prova: {data_prova}
Matéria: {materia}
Área: {area or 'não informada'}

Conteúdos:
{conteudos}

Alta prioridade:
{alta}

Média prioridade:
{media}

Baixa prioridade:
{baixa}

Gerar um plano por dia até a prova.
Formato obrigatório por linha:

DIA X | DATA | CONTEÚDO DO DIA: ... | OBJETIVO: ... | ATIVIDADE: ... | REVISÃO: ... | TEXTO PARA COLAR EM "CONTEÚDO DO DIA": ...

Regras:
- máximo de 1 foco principal por dia
- sessões curtas
- incluir revisão final no dia anterior
- o último dia antes da prova deve ser revisão geral
- o texto para colar deve sair pronto para a aba Configuração
{idioma}
"""
