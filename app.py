import streamlit as st

from src.auth.google_auth import require_login


st.set_page_config(
    page_title="OpenRCA",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =====================================================
# GOOGLE LOGIN
# =====================================================

require_login()


# =====================================================
# USER INFORMATION
# =====================================================

with st.sidebar:

    st.markdown(
        f"### Welcome: {st.user.name}"
    )

    st.caption(
        st.user.email
    )

    st.button(
        "**LOG OUT**",
        on_click=st.logout,
        use_container_width=True
    )

# =====================================================
# MAIN PAGE
# =====================================================

st.title("🔍 OpenRCA")

st.write(
    "Welcome to OpenRCA Incident Investigation System."
)