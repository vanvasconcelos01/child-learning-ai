import streamlit as st
from constants import DEFAULTS

def init_state():
    for k, v in DEFAULTS.items():
        st.session_state.setdefault(k, v)
