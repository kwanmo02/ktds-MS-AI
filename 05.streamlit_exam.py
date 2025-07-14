import streamlit as st
import pandas as pd
import numpy as np
import time

#01 표
df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

df


#02 꺾은선형 차트 그리기
chart_data = pd.DataFrame(
     np.random.randn(20, 3),
     columns=['a', 'b', 'c'])

st.line_chart(chart_data)


#03 지도 플로팅
map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(map_data)


#04 위젯
x = st.slider('x')  # 👈 this is a widget
st.write(x, 'squared is', x * x)


st.text_input("Your name", key="name")
# You can access the value at any point with:
st.session_state.name


#05 진행상황 표시

'Starting a long computation...'

# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
  # Update the progress bar with each iteration.
  latest_iteration.text(f'Iteration {i+1}')
  bar.progress(i + 1)
  time.sleep(0.1)

'...and now we\'re done!'