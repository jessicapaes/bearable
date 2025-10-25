import streamlit as st

st.set_page_config(
    page_title="Test App",
    layout="wide"
)

st.title("Test App")
st.write("If you can see this, Streamlit is working!")

st.markdown("""
<div style="background: red; padding: 20px; color: white;">
    This is a test div
</div>
""", unsafe_allow_html=True)


