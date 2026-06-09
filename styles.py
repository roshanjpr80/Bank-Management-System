import streamlit as st

def apply_style():

    st.markdown("""
    <style>

    .title{
        font-size:30px;
        font-weight:bold;
        color:#1E88E5;
    }

    .stButton>button{
        width:100%;
        border-radius:10px;
    }

    </style>
    """,
    unsafe_allow_html=True)