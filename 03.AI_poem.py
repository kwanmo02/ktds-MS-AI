import openai
from dotenv import load_dotenv
import os

#load environment variables from .env file
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.azure_endpoint = os.getenv("OPENAI_AZURE_ENDPOINT")
openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_version = os.getenv("OPENAI_API_VERSION")

while True:
    subject = input("주제를 입력하세요: ")

    if subject.lower() == "그만":
            print("프로그램을 종료합니다.")
            break

    content = input("시 작성할 내용을 입력하세요: ")
    
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

    print(response.choices[0].message.content)


