import re
import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 2rem;}
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
    }
    .card {
        padding: 16px 18px;
        border-radius: 18px;
        background: white;
        border: 1px solid rgba(15, 23, 42, 0.08);
        box-shadow: 0 6px 24px rgba(15, 23, 42, 0.05);
        margin-bottom: 12px;
    }
    .small {color: #475569; font-size: 0.92rem;}
    h1, h2, h3 {color: #0f172a;}
    hr {
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def slugify(texto: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", texto.strip().lower())

def checkbox_group(label, options, state_key, columns=3):
    st.markdown(f"**{label}**")
    selected_set = set(st.session_state.get(state_key, []))
    cols = st.columns(columns)
    novos_selecionados = []

    for i, option in enumerate(options):
        widget_key = f"{state_key}_{slugify(option)}"
        default_value = option in selected_set

        if widget_key not in st.session_state or not isinstance(st.session_state.get(widget_key), bool):
            st.session_state[widget_key] = default_value

        with cols[i % columns]:
            marcado = st.checkbox(option, key=widget_key)

        if marcado:
            novos_selecionados.append(option)

    st.session_state[state_key] = novos_selecionados

def radio_group(label, options, state_key, horizontal=False):
    valor_atual = st.session_state.get(state_key, options[0])
    if valor_atual not in options:
        valor_atual = options[0]

    st.radio(
        label,
        options,
        index=options.index(valor_atual),
        horizontal=horizontal,
        key=state_key
    )
