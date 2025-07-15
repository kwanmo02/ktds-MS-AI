import requests
import os
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

COMPUTER_VISION_API_KEY = os.getenv("COMPUTER_VISION_API_KEY")
COMPUTER_VISION_ENDPOINT = os.getenv("COMPUTER_VISION_ENDPOINT")

## 이미지 분석
def analyze_image(image_path):
    ENDPOINT_URL = COMPUTER_VISION_ENDPOINT + "vision/v3.2/analyze"
    params = {"visualFeatures": "Categories,Description,Color"}
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

def object_detect(image_path):
    ENDPOINT_URL = COMPUTER_VISION_ENDPOINT + "vision/v3.2/detect"

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
    
    response = requests.post(ENDPOINT_URL, headers=headers, data=image_data) ## 헤더 정보만 넘기면 됌
    
    return response.json()


## 바운딩 박스
def draw_bounding_boxes(image_path, objects):
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image file: {e}")
        return None
    draw = ImageDraw.Draw(image)

    for obj in objects:
        rectangle = obj["rectangle"]
        x, y, w, h = rectangle["x"], rectangle["y"], rectangle["w"], rectangle["h"]
        draw.rectangle([x, y, x + w, y + h], outline="red", width=2)

    prats = image_path.split(".")

    if len(prats) == 2: #확장자가 있다면
        output_path = f"{prats[0]}_detected.{prats[1]}"
    else :
        output_path = f"{image_path}_detected"

    image.save(output_path)
    image.show()

def main():
    image_path = input("Enter the path to the image file: ")

    print("1. Analyzing image...")
    print("2. Object detection...")
    choice = input("Choose an option (1 or 2): ")

    if choice == "1":
        print("Analyzing image...")
        result = analyze_image(image_path)
        print("result", result["description"]["captions"][0]["text"])
    elif choice == "2":
        print("Detecting objects in image...")    
        result = object_detect(image_path)
        draw_bounding_boxes(image_path, result["objects"])
    else :
        print("invalid choice. Please choose 1 for analyzing")
          
if __name__ == "__main__":
    main() #생성자
