import os
os.environ["MPLBACKEND"] = "Agg"  # Ensure non-interactive backend if needed

import streamlit as st

st.title("Hello, World!")
st.write("This is a minimal Streamlit app to test deployment.")
