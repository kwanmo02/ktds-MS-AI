import streamlit as st
import time

st.title("Simple Streamlit App")
st.write("This is a simple Streamlit app to demonstrate basic functionality.")

latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
    #st.write(f"Counter: {i}")
    latest_iteration.text(f"Counter: {i}"+"%")
    time.sleep(1)  # Simulate a delay for demonstration purposes
    bar.progress(i + 1)
    
