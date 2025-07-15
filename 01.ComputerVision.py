import requests
import os
from dotenv import load_dotenv

load_dotenv()

COMPUTER_VISION_API_KEY = os.getenv("COMPUTER_VISION_API_KEY")
COMPUTER_VISION_ENDPOINT = os.getenv("COMPUTER_VISION_ENDPOINT")

def analyze_image(image_path):
    ENDPOINT_URL = COMPUTER_VISION_ENDPOINT + "vision/v3.2/analyze"
    params = {
        "visualFeatures": "Categories,Description,Color"
    },
    headers = {
        "Ocp-Apim-Subscription-Key": COMPUTER_VISION_API_KEY,
        "Content-Type": "application/octet-stream"
    }

    try :
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
    except Exception as e:
        print(f"Error reading image file: {e}")
        return None
    
    response = requests.post(ENDPOINT_URL, params=params, headers=headers, data=image_data)
    
    return response.json()

def main():
    image_path = input("Enter the path to the image file: ")
    result = analyze_image(image_path)
    print("result", result["description"]["captions"][0]["text"])
          
if __name__ == "__main__":
    main() #생성자