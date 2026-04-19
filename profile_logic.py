import json
import re
import datetime
import streamlit as st
from constants import PT_MONTHS, DIAG_CHARACTERISTICS


def _coerce_date(d):
    if isinstance(d, datetime.datetime):
        return d.date()
    if isinstance(d, datetime.date):
        return d
    if isinstance(d, str):
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.datetime.strptime(d, fmt).date()
            except ValueError:
                continue
    return datetime.date.today()


def formatar_data_br(d):
    d = _coerce_date(d)
    return d.strftime("%d/%m/%Y")


def formatar_data_extenso(d):
    d = _coerce_date(d)
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
    items, seen = [], set()
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


def juntar_multiselect_com_outro(lista_base, texto_outro):
    itens = list(lista_base) if lista_base else []
    usar_outro = "Outro" in itens
    itens = [x for x in itens if x != "Outro"]

    if usar_outro and texto_outro and texto_outro.strip():
        itens.append(texto_outro.strip())

    return ", ".join(itens) if itens else "não informado"


def obter_cobranca():
    return juntar_multiselect_com_outro(
        st.session_state.get("cobranca_escola", []),
        st.session_state.get("cobranca_extra", "")
    )


def obter_interesses():
    return juntar_multiselect_com_outro(
        st.session_state.get("interesses", []),
        st.session_state.get("interesses_outro", "")
    )


def obter_tipo_erro():
    return juntar_multiselect_com_outro(
        st.session_state.get("tipo_erro_mais_comum", []),
        st.session_state.get("tipo_erro_outro", "")
    )


def atualizar_caracteristicas_sugeridas():
    st.session_state["caracteristicas_sugeridas"] = combine_characteristics(
        st.session_state.get("diagnosticos", []),
        st.session_state.get("outro_diagnostico", "")
    )


def perfil_aprendizagem_texto():
    engajamento = juntar_multiselect_com_outro(
        st.session_state.get("engajamento", []),
        st.session_state.get("engajamento_outro", "")
    )
    dificuldade = juntar_multiselect_com_outro(
        st.session_state.get("principal_dificuldade", []),
        st.session_state.get("dificuldade_outro", "")
    )
    trava = juntar_multiselect_com_outro(
        st.session_state.get("sinais_quando_trava", []),
        st.session_state.get("trava_outro", "")
    )
    retomada = juntar_multiselect_com_outro(
        st.session_state.get("melhor_forma_retomar", []),
        st.session_state.get("retomada_outro", "")
    )

    return f"""
- Atenção sustentada: {st.session_state.get('atencao_sustentada', 'Média')}
- Autonomia: {st.session_state.get('autonomia', 'Alguma mediação')}
- Canal preferencial: {st.session_state.get('canal_preferencial', 'Visual')}
- Tolerância à frustração: {st.session_state.get('tolerancia_frustracao', 'Média')}
- Leitura: {st.session_state.get('leitura_nivel', 'Adequado')}
- Escrita: {st.session_state.get('escrita_nivel', 'Adequado')}
- Matemática: {st.session_state.get('matematica_nivel', 'Adequado')}
- Compreensão oral: {st.session_state.get('compreensao_oral', 'Média')}
- O que mais engaja: {engajamento}
- Principal dificuldade observada: {dificuldade}
- Tipo de erro mais comum: {obter_tipo_erro()}
- Sinais quando trava: {trava}
- Melhor forma de retomar: {retomada}
""".strip()


def get_perfil_data(data_prova=""):
    diagnosticos = list(st.session_state.get("diagnosticos", []))
    outro = st.session_state.get("outro_diagnostico", "").strip()
    if outro:
        diagnosticos.append(outro)

    atualizar_caracteristicas_sugeridas()

    outras = st.session_state.get("outras_caracteristicas", "").strip()
    sugeridas = st.session_state.get("caracteristicas_sugeridas", "").strip()

    bloco_caracteristicas = sugeridas
    if outras:
        bloco_caracteristicas = f"{sugeridas}; {outras}" if sugeridas else outras

    return {
        "nome": st.session_state.get("nome", ""),
        "apelido": st.session_state.get("apelido", ""),
        "idade": st.session_state.get("idade", ""),
        "serie": st.session_state.get("serie", ""),
        "escola": st.session_state.get("escola", ""),
        "turno": st.session_state.get("turno", ""),
        "interesses": obter_interesses(),
        "responsavel": st.session_state.get("responsavel", ""),
        "diagnosticos": diagnosticos,
        "outras_caracteristicas": bloco_caracteristicas,
        "caracteristicas_sugeridas": sugeridas,
        "perfil_aprendizagem": perfil_aprendizagem_texto(),
        "data_prova": data_prova,
    }


def exportar_perfil_json():
    data = get_perfil_data()
    return json.dumps(data, ensure_ascii=False, indent=2)


def resumo_aluno_compacto(data):
    diags = ", ".join(data["diagnosticos"]) if data["diagnosticos"] else "nenhum"

    engajamento = juntar_multiselect_com_outro(
        st.session_state.get("engajamento", []),
        st.session_state.get("engajamento_outro", "")
    )
    dificuldade = juntar_multiselect_com_outro(
        st.session_state.get("principal_dificuldade", []),
        st.session_state.get("dificuldade_outro", "")
    )
    trava = juntar_multiselect_com_outro(
        st.session_state.get("sinais_quando_trava", []),
        st.session_state.get("trava_outro", "")
    )
    retomada = juntar_multiselect_com_outro(
        st.session_state.get("melhor_forma_retomar", []),
        st.session_state.get("retomada_outro", "")
    )

    return f"""ALUNO
- Nome: {data.get('nome', '') or 'não informado'}
- Apelido: {data.get('apelido', '') or 'não informado'}
- Idade: {data.get('idade', '') or 'não informado'}
- Série: {data.get('serie', '') or 'não informada'}
- Escola: {data.get('escola', '') or 'não informada'}
- Turno: {data.get('turno', '') or 'não informado'}
- Responsável: {data.get('responsavel', '') or 'não informado'}

DIAGNÓSTICOS
- {diags}

INTERESSES
- {data.get('interesses', '') or 'não informado'}

CARACTERÍSTICAS SUGERIDAS DO DIAGNÓSTICO
- {data.get('caracteristicas_sugeridas', '') or 'não informado'}

PERFIL DE APRENDIZAGEM
- Atenção sustentada: {st.session_state.get('atencao_sustentada', 'Média')}
- Autonomia: {st.session_state.get('autonomia', 'Alguma mediação')}
- Canal preferencial: {st.session_state.get('canal_preferencial', 'Visual')}
- Tolerância à frustração: {st.session_state.get('tolerancia_frustracao', 'Média')}
- Leitura: {st.session_state.get('leitura_nivel', 'Adequado')}
- Escrita: {st.session_state.get('escrita_nivel', 'Adequado')}
- Matemática: {st.session_state.get('matematica_nivel', 'Adequado')}
- Compreensão oral: {st.session_state.get('compreensao_oral', 'Média')}
- O que mais engaja: {engajamento}
- Principal dificuldade: {dificuldade}
- Tipo de erro mais comum: {obter_tipo_erro()}
- Sinais quando trava: {trava}
- Melhor forma de retomar: {retomada}

OUTRAS CARACTERÍSTICAS
- {st.session_state.get('outras_caracteristicas', '') or 'não informado'}
"""


def extrair_campos_cronograma(linha):
    resultado = {
        "conteudo": "",
        "objetivo": "",
        "atividade": "",
        "revisao": "",
        "texto_colar": ""
    }

    padroes = {
        "conteudo": r"CONTEÚDO DO DIA:\s*(.*?)\s*(?:\||$)",
        "objetivo": r"OBJETIVO:\s*(.*?)\s*(?:\||$)",
        "atividade": r"ATIVIDADE:\s*(.*?)\s*(?:\||$)",
        "revisao": r"REVISÃO:\s*(.*?)\s*(?:\||$)",
        "texto_colar": r'TEXTO PARA COLAR EM "CONTEÚDO DO DIA":\s*(.*)'
    }

    for chave, padrao in padroes.items():
        match = re.search(padrao, linha, flags=re.IGNORECASE)
        if match:
            resultado[chave] = match.group(1).strip()

    return resultado
