




import streamlit as st

def apply_style():
    st.markdown("""
        <style>
            .title {
                font-size: 32px;
                font-weight: 700;
                color: #2C3E50;
                margin-bottom: 20px;
            }
            .stButton>button {
                background-color: #2C3E50;
                color: white;
                padding: 10px 25px;
                border-radius: 8px;
                font-size: 16px;
            }
            .stTextInput>div>div>input {
                border-radius: 8px;
                padding: 8px;
            }
            .subtitle { color:#FFD500; font-size:20px; font-weight:bold; }
            .success { color:#00FF84; }
            .error { color:#FF4C4C; }
        </style>
    """, unsafe_allow_html=True)

