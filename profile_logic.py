import json
import re
import streamlit as st
from constants import PT_MONTHS, DIAG_CHARACTERISTICS

def formatar_data_br(d):
    return d.strftime("%d/%m/%Y")

def formatar_data_extenso(d):
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
        st.session_state["cobranca_escola"],
        st.session_state["cobranca_extra"]
    )

def obter_interesses():
    return juntar_multiselect_com_outro(
        st.session_state["interesses"],
        st.session_state["interesses_outro"]
    )

def obter_tipo_erro():
    erro = st.session_state["tipo_erro_mais_comum"]
    if erro == "Outro" and st.session_state["tipo_erro_outro"].strip():
        return st.session_state["tipo_erro_outro"].strip()
    return erro

def atualizar_caracteristicas_sugeridas():
    st.session_state["caracteristicas_sugeridas"] = combine_characteristics(
        st.session_state["diagnosticos"],
        st.session_state.get("outro_diagnostico", "")
    )

def perfil_aprendizagem_texto():
    engajamento = juntar_multiselect_com_outro(
        st.session_state["engajamento"],
        st.session_state["engajamento_outro"]
    )
    dificuldade = juntar_multiselect_com_outro(
        st.session_state["principal_dificuldade"],
        st.session_state["dificuldade_outro"]
    )
    trava = juntar_multiselect_com_outro(
        st.session_state["sinais_quando_trava"],
        st.session_state["trava_outro"]
    )
    retomada = juntar_multiselect_com_outro(
        st.session_state["melhor_forma_retomar"],
        st.session_state["retomada_outro"]
    )

    return f"""
- Atenção sustentada: {st.session_state['atencao_sustentada']}
- Autonomia: {st.session_state['autonomia']}
- Canal preferencial: {st.session_state['canal_preferencial']}
- Tolerância à frustração: {st.session_state['tolerancia_frustracao']}
- Leitura: {st.session_state['leitura_nivel']}
- Escrita: {st.session_state['escrita_nivel']}
- Matemática: {st.session_state['matematica_nivel']}
- Compreensão oral: {st.session_state['compreensao_oral']}
- O que mais engaja: {engajamento}
- Principal dificuldade observada: {dificuldade}
- Tipo de erro mais comum: {obter_tipo_erro()}
- Sinais quando trava: {trava}
- Melhor forma de retomar: {retomada}
""".strip()

def get_perfil_data(data_prova=""):
    diagnosticos = list(st.session_state["diagnosticos"])
    if st.session_state["outro_diagnostico"].strip():
        diagnosticos.append(st.session_state["outro_diagnostico"].strip())

    atualizar_caracteristicas_sugeridas()

    outras = st.session_state["outras_caracteristicas"].strip()
    sugeridas = st.session_state["caracteristicas_sugeridas"].strip()

    bloco_caracteristicas = sugeridas
    if outras:
        bloco_caracteristicas = f"{sugeridas}; {outras}" if sugeridas else outras

    return {
        "nome": st.session_state["nome"],
        "apelido": st.session_state["apelido"],
        "idade": st.session_state["idade"],
        "serie": st.session_state["serie"],
        "escola": st.session_state["escola"],
        "turno": st.session_state["turno"],
        "interesses": obter_interesses(),
        "responsavel": st.session_state["responsavel"],
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
        st.session_state["engajamento"],
        st.session_state["engajamento_outro"]
    )
    dificuldade = juntar_multiselect_com_outro(
        st.session_state["principal_dificuldade"],
        st.session_state["dificuldade_outro"]
    )
    trava = juntar_multiselect_com_outro(
        st.session_state["sinais_quando_trava"],
        st.session_state["trava_outro"]
    )
    retomada = juntar_multiselect_com_outro(
        st.session_state["melhor_forma_retomar"],
        st.session_state["retomada_outro"]
    )

    return f"""ALUNO
- Nome: {data['nome'] or 'não informado'}
- Apelido: {data['apelido'] or 'não informado'}
- Idade: {data['idade'] or 'não informado'}
- Série: {data['serie'] or 'não informada'}
- Escola: {data['escola'] or 'não informada'}
- Turno: {data['turno'] or 'não informado'}
- Responsável: {data['responsavel'] or 'não informado'}

DIAGNÓSTICOS
- {diags}

INTERESSES
- {data['interesses'] or 'não informado'}

CARACTERÍSTICAS SUGERIDAS DO DIAGNÓSTICO
- {data.get('caracteristicas_sugeridas', '') or 'não informado'}

PERFIL DE APRENDIZAGEM
- Atenção sustentada: {st.session_state['atencao_sustentada']}
- Autonomia: {st.session_state['autonomia']}
- Canal preferencial: {st.session_state['canal_preferencial']}
- Tolerância à frustração: {st.session_state['tolerancia_frustracao']}
- Leitura: {st.session_state['leitura_nivel']}
- Escrita: {st.session_state['escrita_nivel']}
- Matemática: {st.session_state['matematica_nivel']}
- Compreensão oral: {st.session_state['compreensao_oral']}
- O que mais engaja: {engajamento}
- Principal dificuldade: {dificuldade}
- Tipo de erro mais comum: {obter_tipo_erro()}
- Sinais quando trava: {trava}
- Melhor forma de retomar: {retomada}

OUTRAS CARACTERÍSTICAS
- {st.session_state['outras_caracteristicas'] or 'não informado'}
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
