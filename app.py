from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import requests
from io import BytesIO

app = Flask(__name__)

@app.route('/api/image-to-text', methods=['POST'])
def image_to_text_api():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    image_file = request.files['image']
    img = Image.open(image_file)
    text = pytesseract.image_to_string(img, lang='vie')
    return jsonify({'extracted_text': text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 