import streamlit as st


def require_login():

    if not st.user.is_logged_in:

        st.button(
            "🔐 Sign in with Google",
            on_click=st.login,
            args=("google",),
            width="content"
        )

        st.stop()