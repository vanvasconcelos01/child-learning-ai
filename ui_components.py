import re
import streamlit as st


def inject_styles():
    st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
    }

    .small {
        color: #475569;
        font-size: 0.92rem;
    }

    h1, h2, h3 {
        color: #0f172a;
    }

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

    if state_key not in st.session_state or not isinstance(st.session_state[state_key], list):
        st.session_state[state_key] = []

    selecionados = set(st.session_state[state_key])
    cols = st.columns(columns)
    novos_selecionados = []

    for i, option in enumerate(options):
        widget_key = f"{state_key}_{slugify(option)}"

        valor_atual = st.session_state.get(widget_key, option in selecionados)
        if not isinstance(valor_atual, bool):
            valor_atual = option in selecionados
            st.session_state[widget_key] = valor_atual

        with cols[i % columns]:
            marcado = st.checkbox(
                label=option,
                value=valor_atual,
                key=widget_key
            )

        if marcado:
            novos_selecionados.append(option)

    st.session_state[state_key] = novos_selecionados


def radio_group(label, options, state_key, horizontal=False):
    if state_key not in st.session_state or st.session_state[state_key] not in options:
        st.session_state[state_key] = options[0]

    st.radio(
        label=label,
        options=options,
        index=options.index(st.session_state[state_key]),
        key=state_key,
        horizontal=horizontal,
    )
