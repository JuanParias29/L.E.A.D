import streamlit as st

st.set_page_config(page_title="L.E.A.D Forecasting", layout="wide")

st.title("L.E.A.D — Forecasting MVP")

st.markdown("This is a minimal Streamlit scaffold. Replace with your app code.")

if st.button("Run sample prediction"):
    st.info("Prediction run placeholder — implement `src/forecasting/predict.py` call here.")
