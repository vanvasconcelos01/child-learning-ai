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
    if "arte" in m:
        return "Especialista em Artes, leitura de imagem, expressão artística e elementos visuais."

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


def compact_student_block(data):
    diags = ", ".join(data["diagnosticos"]) if data["diagnosticos"] else "nenhum"
    return (
        f"Aluno: {data['nome'] or 'não informado'} | Idade: {data['idade'] or 'não informado'} | Série: {data['serie'] or 'não informado'}\n"
        f"Diagnósticos: {diags}\n"
        f"Características: {data.get('caracteristicas_sugeridas', 'não informado') or 'não informado'}\n"
        f"Interesses: {data['interesses'] or 'não informado'}\n"
        f"Perfil de aprendizagem:\n{data['perfil_aprendizagem']}"
    )


def contexto_curto(data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes):
    especialidade = get_subject_specialization(materia, area)
    idioma = get_language_support_instruction(materia, area)
    anexos = "usar anexos só como embasamento; material final autossuficiente" if usa_fontes else "criar sem anexos; material final autossuficiente"

    return f"""NOTEBOOKLM STUDIO

Matéria: {materia or 'não informada'}
Área: {area or 'não informada'}
Conteúdo do dia: {conteudo or 'não informado'}
Objetivo do dia: {objetivo or 'não informado'}
Dias até a prova: {dias}
Situação: {situacao}
Prioridade: {prioridade}
Como a escola cobra: {estilo or 'não informado'}
Anexos: {anexos}

Especialidade:
{especialidade}

Aluno:
{compact_student_block(data)}

Regras fixas:
- usar somente o conteúdo do dia
- alinhar ao que costuma ser mais cobrado para a idade/série dentro do repertório dado
- material totalmente autossuficiente
- não depender de página, imagem, capítulo, trecho ou tela do livro
- não escrever: "observe a página", "veja a imagem", "como mostrado acima"
- preservar exatamente os termos oficiais do conteúdo
- não inventar nomes novos para conceitos, categorias ou classificações
{idioma}
"""


def prompt_video(data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn=None):
    return contexto_curto(
        data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes
    ) + """
Tarefa: gerar VIDEO OVERVIEW final.

Exigências:
- vídeo curto
- explicar apenas o conteúdo do dia
- NÃO usar, mostrar, destacar ou enquadrar fotos/páginas/imagens do livro ou anexo
- reconstruir tudo com cenas próprias, exemplos próprios e visuais próprios
- manter os termos oficiais do conteúdo
- não inventar termos substitutos
- quando fizer pergunta, esperar cerca de 3 segundos antes de continuar
- fechar com mini revisão
"""


def prompt_audio(data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn=None):
    return contexto_curto(
        data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes
    ) + """
Tarefa: gerar AUDIO OVERVIEW final para o responsável.

Exigências:
- áudio direto e objetivo
- duração alvo: 2 a 3 minutos
- foco apenas no conteúdo do dia
- resumir o que deve ser estudado hoje
- explicar como conduzir a atividade
- apontar rapidamente onde o aluno pode travar
- indicar como retomar de forma simples
- manter os termos oficiais do conteúdo
- não inventar termos substitutos
- evitar introduções longas, exemplos excessivos e aprofundamentos desnecessários
"""


def prompt_slides(data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn=None):
    return contexto_curto(
        data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes
    ) + """
Tarefa: gerar SLIDES finais.

Exigências:
- usar apenas o conteúdo do dia
- progressão: conceito, exemplo, erro comum, aplicação, revisão
- exemplos próprios
- sem telas do livro
- preservar os termos oficiais do conteúdo
- pouco texto por slide
"""


def prompt_flash(data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn=None):
    return contexto_curto(
        data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes
    ) + """
Tarefa: gerar FLASHCARDS finais.

Exigências obrigatórias:
- entregar EXATAMENTE 10 flashcards
- nem 9, nem 11, nem mais
- usar apenas o conteúdo do dia
- não expandir para outros conteúdos
- focar no mais importante, mais cobrado e mais sujeito a erro
- preservar os termos oficiais do conteúdo

Formato:
1. Frente: ...
   Verso: ...
2. Frente: ...
   Verso: ...
...
10. Frente: ...
    Verso: ...
"""


def prompt_teste(data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes, resumo_aluno_fn=None):
    return contexto_curto(
        data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, usa_fontes
    ) + """
Tarefa: gerar TESTE final.

Exigências:
- usar apenas o conteúdo do dia
- gerar 5 questões
- adaptar ao formato de cobrança da escola
- incluir gabarito comentado
- preservar termos oficiais do conteúdo
"""


def prompt_aula(data, materia, area, conteudo, objetivo, estilo, situacao, prioridade, dias, selected, usa_fontes, modo_estudo_fn):
    base = f"""AULA COMPLETA

Matéria: {materia}
Área: {area or 'não informada'}
Conteúdo do dia: {conteudo}
Objetivo do dia: {objetivo or 'não informado'}
Dias até a prova: {dias}
Situação: {situacao}
Prioridade: {prioridade}
Modo de estudo: {modo_estudo_fn(dias, situacao)}
Como a escola cobra: {estilo or 'não informado'}

Regras:
- usar só o conteúdo do dia
- preservar termos oficiais
- não inventar conceitos
- material autossuficiente
"""

    parts = [base]

    if "Vídeo" in selected:
        parts.append("[VIDEO OVERVIEW]\n- vídeo curto, com cenas próprias, sem imagens do livro e com pausas após perguntas")
    if "Áudio (responsável)" in selected:
        parts.append("[AUDIO OVERVIEW]\n- áudio curto, 2 a 3 minutos, direto e objetivo")
    if "Slides" in selected:
        parts.append("[SLIDES]\n- slides autossuficientes, sem depender do livro")
    if "Flashcards (máx 10)" in selected:
        parts.append("[FLASHCARDS]\n- EXATAMENTE 10 cards, apenas do conteúdo do dia")
    if "Teste" in selected:
        parts.append("[TESTE]\n- 5 questões com gabarito")

    return "\n\n".join(parts)


def prompt_cronograma(data, materia, area, conteudos, data_hoje, data_prova, alta, media, baixa):
    especialidade = get_subject_specialization(materia, area)
    idioma = get_language_support_instruction(materia, area)

    return f"""PERFIL DO ALUNO
Aluno: {data['nome']} ({data['apelido']})
Idade: {data['idade']}
Série: {data['serie']}

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
