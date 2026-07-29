import streamlit as st


def require_login():

    if not st.user.is_logged_in:

        st.title("OpenRCA - DTH")

        st.write(
            "Please sign in with Google"
        )

        st.button(
            "Sign in with Google",
            on_click=st.login,
            args=["google"]
        )

        st.stop()