import streamlit as st
from constants import DEFAULTS, LEGACY_KEY_MAP

def init_state():
    for k, v in DEFAULTS.items():
        st.session_state.setdefault(k, v)

def migrate_legacy_keys():
    for old_key, new_key in LEGACY_KEY_MAP.items():
        old_val = st.session_state.get(old_key, "")
        new_val = st.session_state.get(new_key, "")
        if (not new_val) and old_val:
            st.session_state[new_key] = old_val
