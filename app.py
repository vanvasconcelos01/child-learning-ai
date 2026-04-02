def prompt_cronograma(data,materia,conteudos,data_hoje,data_prova,alta,media,baixa):
    return f"""{build_base_prompt(data)}

MATERIAL: CRONOGRAMA ESTRATÉGICO ATÉ A PROVA

CONTEXTO
Data de hoje: {data_hoje}
Data da prova: {data_prova}
Matéria: {materia}
Série: {data['serie']}

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
