import streamlit as st

from src.auth.google_auth import require_login


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="OpenRCA",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =====================================================
# LANDING PAGE
# =====================================================

st.markdown(
    """
    <div style="text-align:center">

    <h1>🔍 OpenRCA - AI-powered Root Cause Analysis Platform </h1>

    <p>
    Final Capstone Project - DTH Team
    </p>

    </div>
    """,
    unsafe_allow_html=True
)


st.write("")


st.markdown(
    """
    <div style="text-align:center; font-size:18px">

    OpenRCA helps teams report incidents,
    investigate system issues, and generate
    Root Cause Analysis reports with evidence.

    </div>
    """,
    unsafe_allow_html=True
)


st.write("")
st.divider()


# =====================================================
# GOOGLE LOGIN
# =====================================================

require_login()


# =====================================================
# SIDEBAR (AFTER LOGIN)
# =====================================================

with st.sidebar:

    st.markdown("## 👋 Welcome")

    st.write(f"**{st.user.name}**")

    st.caption(st.user.email)

    st.divider()

    st.button(
        "🚪 Log Out",
        on_click=st.logout,
        use_container_width=True
    )


# =====================================================
# HOME CONTENT AFTER LOGIN
# =====================================================


st.markdown("## 👋 Welcome to OpenRCA")

st.write(
    f"""
    Hello **{st.user.name}**

    Use the sidebar to navigate through the platform.
    """
)