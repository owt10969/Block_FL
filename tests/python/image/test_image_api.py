import requests
import base64
import os
import io
import cv2
import numpy as np
from PIL import Image
from io import BytesIO


def test_image_api():
    url = "http://localhost:8080/encode/image/print/raw"
    image_path = "test.jpg"

    if not os.path.exists(image_path):
        print(f"Error for finding test.jpg at {image_path}")
        return
    
    files = {'image':('test.jpg', open(image_path, 'rb'), 'image/jpeg')}
    
    try:
        response = requests.get(url, files = files)

        if response.status_code == 200:
            result = response.json()
            #print(result)
            print("Vector:", result.get ("vector"))
            print(f"process_id: {result.get('process_id')}")
            image_data = base64.b64decode(result.get("EncodeBytes"))

            with Image.open(image_path) as img:
                width, height = img.size
                print("\nActual Image Info:")
                print(f"Width: {width}")
                print(f"Height: {height}")
                print(f"Aspect Ratio: {width/height}")
            
            #image = Image.open(BytesIO(image_data))
            #image.show()

            # Use OpenCV
            nparr = np.frombuffer(image_data, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            cv2.imshow('Decoded Image', img_np)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    except Exception as e:
        print(f"Exception code : {e}")

if __name__ == "__main__":
    test_image_api()