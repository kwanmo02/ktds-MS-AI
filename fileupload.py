import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

#load_dotenv()  # 환경변수 로드

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_BLOB_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER")

try:
    #blob 스토리지 연결
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING) 
    container_client = blob_service_client.get_container_client(AZURE_BLOB_CONTAINER)

    #업로드 할 이름
    blob_client = container_client.get_blob_client("치타.jpg")

    #File upload example
    with open(r"C:\Users\ktds\Desktop\ktds_km_webapp\치타.jpg", "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print("File uploaded successfully.")

except Exception as e:
    print(f"Error loading environment variables: {e}") 