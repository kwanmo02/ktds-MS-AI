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
    # Get user input for the question
    questions = input("질문을 입력하세요: ")
    if questions.lower() == "그만":
        print("프로그램을 종료합니다.")
        break

    response=openai.chat.completions.create(
        model="dev-gpt-4o-mini",
        messages=[
            {"role": "system", "content": "you are a helpful assistant."},
            {"role": "user", "content": questions}
        ]
    )

    print(response.choices[0].message.content)


