PT_MONTHS = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}

STEPS = [
    "Perfil",
    "Aprendizagem",
    "Cronograma",
    "Configuração",
    "Studio",
    "Aula Completa"
]

INTERESSES_OPTIONS = [
    "games", "Minecraft", "Roblox", "Pokémon", "futebol",
    "animais", "dinossauros", "espaço", "ciência",
    "arte", "música", "livros", "aventura", "Outro"
]

DIAG_OPTIONS = [
    "TDAH",
    "TEA nível 1",
    "Dislexia",
    "Discalculia",
    "Processamento auditivo",
    "Ansiedade",
    "Outro"
]

DIAG_CHARACTERISTICS = {
    "TDAH": [
        "atenção curta",
        "beneficia-se de blocos curtos",
        "precisa de ritmo dinâmico",
        "responde melhor a objetivos claros"
    ],
    "Dislexia": [
        "beneficia-se de menor carga textual",
        "precisa de apoio visual",
        "frases mais curtas"
    ],
    "Discalculia": [
        "precisa de apoio concreto",
        "progressão gradual",
        "exemplos visuais"
    ],
    "Processamento auditivo": [
        "beneficia-se de apoio visual constante",
        "mensagens curtas",
        "ver e ouvir ao mesmo tempo ajuda"
    ],
    "Ansiedade": [
        "pode travar sob pressão",
        "precisa de previsibilidade",
        "erro deve ser tratado com calma"
    ]
}

ESCOLA_COBRANCA_OPTIONS = [
    "questões objetivas",
    "questões dissertativas curtas",
    "interpretação de texto",
    "interpretação com imagens",
    "mapas, gráficos ou tabelas",
    "vocabulário e definições",
    "Outro"
]

ATENCAO_OPTIONS = ["Muito baixa", "Baixa", "Média", "Boa"]
AUTONOMIA_OPTIONS = ["Precisa de muita mediação", "Alguma mediação", "Quase independente"]
CANAL_OPTIONS = ["Visual", "Auditivo", "Misto"]
FRUSTRACAO_OPTIONS = ["Baixa", "Média", "Boa"]
NIVEL_OPTIONS = ["Abaixo do esperado", "Adequado", "Acima do esperado"]

ERRO_OPTIONS = ["trava", "chuta", "dispersa", "fica ansioso", "Outro"]
ENGAJAMENTO_OPTIONS = ["jogos", "quiz", "visual", "desafios curtos", "Outro"]
DIFICULDADE_OPTIONS = [
    "manter atenção",
    "interpretar texto",
    "memorizar",
    "resolver sozinho",
    "Outro"
]
TRAVA_OPTIONS = [
    "fica em silêncio",
    "diz que não sabe",
    "pede ajuda",
    "quer parar",
    "Outro"
]
RETOMADA_OPTIONS = [
    "dividir em partes",
    "usar apoio visual",
    "dar exemplo",
    "retomar do último acerto",
    "Outro"
]

SITUACAO_OPTIONS = ["novo", "ja_visto", "em_dificuldade"]
PRIORIDADE_OPTIONS = ["alta", "media", "baixa"]

AREA_MATERIA_OPTIONS = [
    "",
    "Linguagens",
    "Exatas",
    "Ciências da Natureza",
    "Humanas",
    "Idiomas",
    "Artes"
]

DEFAULTS = {
    "current_step": "Perfil",

    "nome": "",
    "apelido": "",
    "idade": "",
    "serie": "",
    "escola": "",
    "turno": "",
    "responsavel": "",

    "interesses": [],
    "interesses_outro": "",

    "diagnosticos": [],
    "outro_diagnostico": "",
    "caracteristicas_sugeridas": "",
    "outras_caracteristicas": "",

    "atencao_sustentada": "Média",
    "autonomia": "Alguma mediação",
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
    "cron_area_materia": "",
    "cron_conteudos": "",
    "cron_alta": "",
    "cron_media": "",
    "cron_baixa": "",
    "cronograma_linha_do_dia": "",

    "mat_did": "",
    "config_area_materia": "",
    "conteudo_dia": "",
    "objetivo_dia": "",
    "situacao_conteudo": "novo",
    "prioridade_conteudo": "alta",

    "usa_fontes": False,
    "selected_materials": ["Vídeo", "Slides", "Teste"],

    "cobranca_escola": [],
    "cobranca_extra": ""
}
