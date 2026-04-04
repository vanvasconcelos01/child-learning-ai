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
    "games", "histórias de fantasia", "futebol", "Pokémon", "música", "desenhos",
    "arte", "animais", "dinossauros", "super-heróis", "Minecraft", "Roblox",
    "ciência", "espaço", "mistério", "aventura", "livros", "corridas",
    "dança", "tecnologia", "Outro"
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
ERRO_OPTIONS = [
    "trava",
    "chuta",
    "dispersa",
    "fica ansioso",
    "recusa",
    "Outro"
]

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
    "tipo_erro_mais_comum": [],
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
