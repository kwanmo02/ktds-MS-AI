import os
from dotenv import load_dotenv
from openai import AzureOpenAI

def main():
    os.system("cls" if os.name == "nt" else "clear")

    load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
    CHAT_DEPLOYMENT_NAME = os.getenv("CHAT_DEPLOYMENT_NAME")
    EMBEDDING_DEPLOYMENT_NAME = os.getenv("EMBEDDING_DEPLOYMENT_NAME")

    AI_SEARCH_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT")
    AI_SEARCH_QUERY_KEY = os.getenv("AI_SEARCH_QUERY_KEY")
    AI_SEARCH_INDEX_NAME = os.getenv("AI_SEARCH_INDEX_NAME")

    print(AI_SEARCH_ENDPOINT)
    print(AI_SEARCH_QUERY_KEY)
    print(AI_SEARCH_INDEX_NAME)

    # Initialize OpenAI client
    # Initialize Azure OpenAI client
    chat_client = AzureOpenAI(
        api_version="2024-12-01-preview",
        azure_endpoint=AZURE_ENDPOINT,
        api_key=OPENAI_API_KEY,
    )

    # Initialize prompt with system message
    prompt = [
        {
            "role": "system",
            "content": "You are a travel assistant. that provides information on travel services"
        }
    ]

    while True:
        input_text = input("Enter your question (or type 'exit' to quit): ")
        if input_text.lower() == 'exit':
            break
        elif input_text.strip() == "":
            print("Please enter a valid question.")
            continue

        prompt.append({"role": "user", "content": input_text})

         # Additional parameters to apply RAG pattern using the AI Search index
        rag_params = {
            "data_sources": [
                {
                    # The following params are used to search the index (keyword search)
                    "type": "azure_search",
                    "parameters": {
                        "endpoint": AI_SEARCH_ENDPOINT,
                        "index_name": AI_SEARCH_INDEX_NAME,
                        "authentication": {
                            "type": "api_key",
                            "key": AI_SEARCH_QUERY_KEY,
                        },
                        # Use simple keyword search instead of vector search
                        "query_type": "simple",
                    }
                }
            ],
        }

        # submit the prompt to the chat client
        response = chat_client.chat.completions.create(
            model=CHAT_DEPLOYMENT_NAME,
            messages=prompt,
            extra_body=rag_params,
        )

        completion = response.choices[0].message.content
        print(f"AI Response: {completion}")

        prompt.append({"role": "assistant", "content": completion})

if __name__ == "__main__":
    main()