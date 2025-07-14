import openai
from dotenv import load_dotenv
import os

#load environment variables from .env file
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.azure_endpoint = os.getenv("OPENAI_AZURE_ENDPOINT")
openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_version = os.getenv("OPENAI_API_VERSION")

response=openai.chat.completions.create(
    model="dev-gpt-4o-mini",
    messages=[
        {"role": "user", "content": "이순신 장군이 누구야?"},
        {"role": "system", "content": "you are a helpful assistant."}
    ]

)

#print(response)

#for i in response.choices:
    #iresponse.choices[0].message.content

print(response.choices[0].message.content)


