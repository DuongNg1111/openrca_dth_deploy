import streamlit as st
import streamlit as st

from src.auth.google_auth import require_login


require_login()

st.title("⚙️ Settings")

st.write("Coming soon...")