import openai
from dotenv import load_dotenv
import os
import streamlit as st
import time

#load environment variables from .env file
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.azure_endpoint = os.getenv("OPENAI_AZURE_ENDPOINT")
openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_version = os.getenv("OPENAI_API_VERSION")


subject = st.text_input("주제를 입력하세요: ")  ##### 변경 됌 #####
content = st.text_area("시 작성할 내용을 입력하세요: ")  ##### 변경 됌 #####

if st.button("시 작성하기"):
    if not subject or not content:
        st.warning("주제와 내용을 모두 입력해주세요.")
        st.stop()
    else:
        #st.success("시를 작성 중입니다...")
        with st.spinner("Wait for it...", show_time=True):
            time.sleep(5)

    response=openai.chat.completions.create(
        model="dev-gpt-4o-mini",
        temperature=0.7, #1에 갈수로 감성적임(없는 내용으로 오버함)
        max_tokens=300, #시의 길이
        messages=[
            {"role": "system", "content": "you are a AI poem."},
            {"role": "user", "content": "주제 : " + subject + 
                                        "\n내용 : " + content + 
                                        "\n시를 작성해줘."}
        ]
    )

    st.write(response.choices[0].message.content)  ##### 변경 됌 #####


