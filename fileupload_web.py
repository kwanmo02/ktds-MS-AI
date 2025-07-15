import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import streamlit as st


######streamlit을 활용하여 별도 웹에서 Azure Blob Storage에 파일 업로드 기능 구현######


load_dotenv()  # 환경변수 로드

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_BLOB_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER")

st.title("file upload to Azure Blob Storage") 
uploaded_file = st.file_uploader("Choose a file", type=["jpg", "png", "jpeg"]) #확장자 제약

if uploaded_file is not None:
    try:
        # blob 스토리지 연결
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING) 
        container_client = blob_service_client.get_container_client(AZURE_BLOB_CONTAINER)

        # 업로드 할 이름
        blob_client = container_client.get_blob_client(uploaded_file.name)

        # Upload the file to Azure Blob Storage
        blob_client.upload_blob(uploaded_file, overwrite=True)
        st.success("File uploaded successfully.")
    except Exception as e:
        st.error(f"Error uploading file: {e}")
