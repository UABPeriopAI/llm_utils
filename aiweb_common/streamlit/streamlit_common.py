import streamlit as st

<<<<<<< HEAD

=======
#Depricated in prefrence for page_renderer - keeping around to ensure compatibility.
>>>>>>> develop
def hide_streamlit_branding():
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def apply_uab_font():
    streamlit_style = """
            <style>
            html, body, [class*="css"]  {
            font-family: proxima-nova, sans-serif;
            }
            </style>
            """
    st.markdown(streamlit_style, unsafe_allow_html=True)
