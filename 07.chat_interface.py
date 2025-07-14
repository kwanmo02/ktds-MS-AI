import openai
from dotenv import load_dotenv
import os
import streamlit as st

#load environment variables from .env file
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.azure_endpoint = os.getenv("OPENAI_AZURE_ENDPOINT")
openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_version = os.getenv("OPENAI_API_VERSION")

def get_openai_client(messages):
    try:
        response = openai.chat.completions.create(
            model="dev-gpt-4o-mini",
            messages=messages,
            temperature=0.7,  # 1에 갈수로 감성적임(없는 내용으로 오버함)
            max_tokens=300,  # 시의 길이
        )
        return response.choices[0].message.content

    except Exception as e:
        st.error(f"OpenAI API 호출 중 오류 발생: {e}")
        return f"Error: {e}"

# Streamlit UI
st.title("Azure OpenAI Chat Interface")
st.write("질문을 입력하고 답변을 받아보세요.")

# 세션에 메시지 저장
# 저장 가능한 메모리 생성
if 'messages' not in st.session_state:
    st.session_state.messages = []
###
# 채팅 메시지 표시    
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# 사용자 입력 받기
if user_input := st.chat_input("메시지를 입력하세요: "): #text_input이 아닌 chat_input 사용
    st.session_state.messages.append({"role": "user", "content": user_input})  # 메모리에만 저장된 상태
    st.chat_message("user").write(user_input) #user_input이 chat_message로 표시됨

    ##대답이 오기 전까지 로딩 표시
    with st.spinner("답변 생각중..."):
        assistant_response = get_openai_client(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})  # 메모리에만 저장된 상태
    st.chat_message("assistant").write(assistant_response)  # assistant의 답변 표시