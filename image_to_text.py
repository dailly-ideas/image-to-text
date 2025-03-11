from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Cấu hình thư mục tải lên tạm thời
UPLOAD_FOLDER = '/tmp/ocr_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Danh sách các ngôn ngữ được hỗ trợ
SUPPORTED_LANGUAGES = {
    'vie': 'Vietnamese',
    'eng': 'English',
    'chi_sim': 'Chinese Simplified',
    'chi_tra': 'Chinese Traditional',
    'jpn': 'Japanese',
    'kor': 'Korean',
    'tha': 'Thai',
    'ara': 'Arabic',
    'fra': 'French',
    'deu': 'German',
    'spa': 'Spanish',
    'rus': 'Russian',
    'hin': 'Hindi'
}

def preprocess_image(image_path, lang):
    """Xử lý trước hình ảnh để cải thiện kết quả OCR"""
    img = cv2.imread(image_path)
    
    # Chuyển sang grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Áp dụng các kỹ thuật tiền xử lý khác nhau dựa trên ngôn ngữ
    if lang in ['chi_sim', 'chi_tra', 'jpn', 'kor']:
        # Tối ưu cho các ngôn ngữ Đông Á
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
    elif lang in ['ara', 'hin']:
        # Tối ưu cho các ngôn ngữ có nhiều đường cong và dấu
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(gray, kernel, iterations=1)
        thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    else:
        # Xử lý mặc định cho các ngôn ngữ Latin
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    # Lưu hình ảnh đã xử lý
    processed_path = image_path + "_processed.jpg"
    cv2.imwrite(processed_path, thresh)
    
    return processed_path

@app.route('/api/supported-languages', methods=['GET'])
def get_supported_languages():
    """Trả về danh sách các ngôn ngữ được hỗ trợ"""
    return jsonify(SUPPORTED_LANGUAGES)

@app.route('/api/image-to-text', methods=['POST'])
def image_to_text_api():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
        
    # Lấy file hình ảnh
    image_file = request.files['image']
    
    # Lấy tham số ngôn ngữ từ form data, mặc định là 'eng' (tiếng Anh)
    language = request.form.get('language', 'eng')
    
    if language not in SUPPORTED_LANGUAGES:
        return jsonify({
            'error': f'Unsupported language code: {language}. Supported languages: {", ".join(SUPPORTED_LANGUAGES.keys())}'
        }), 400
    
    # Lưu file tạm thời
    filename = secure_filename(image_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_file.save(file_path)
    
    try:
        # Tiền xử lý hình ảnh nếu được yêu cầu
        preprocess = request.form.get('preprocess', 'true').lower() == 'true'
        
        if preprocess:
            processed_path = preprocess_image(file_path, language)
            img = Image.open(processed_path)
        else:
            img = Image.open(file_path)
        
        # Cấu hình OCR
        custom_config = request.form.get('config', '')
        
        # Trích xuất văn bản với ngôn ngữ đã chọn
        text = pytesseract.image_to_string(img, lang=language, config=custom_config)
        
        # Nếu ngôn ngữ là Đông Á, dùng thêm PSM khác để so sánh kết quả
        alternative_text = None
        if language in ['chi_sim', 'chi_tra', 'jpn', 'kor']:
            # Thử với Page Segmentation Mode khác cho các ngôn ngữ Đông Á
            alternative_text = pytesseract.image_to_string(
                img, 
                lang=language, 
                config='--psm 6'  # Giả định trang là một khối văn bản duy nhất
            )
        
        result = {
            'extracted_text': text,
            'language': language,
            'language_name': SUPPORTED_LANGUAGES[language]
        }
        
        if alternative_text:
            result['alternative_text'] = alternative_text
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Dọn dẹp file tạm thời
        if os.path.exists(file_path):
            os.remove(file_path)
        
        processed_path = file_path + "_processed.jpg"
        if os.path.exists(processed_path):
            os.remove(processed_path)

@app.route('/api/batch-process', methods=['POST'])
def batch_process():
    """Xử lý nhiều hình ảnh cùng lúc với cùng một ngôn ngữ"""
    if 'images' not in request.files:
        return jsonify({'error': 'No images provided'}), 400
    
    images = request.files.getlist('images')
    language = request.form.get('language', 'eng')
    
    if language not in SUPPORTED_LANGUAGES:
        return jsonify({
            'error': f'Unsupported language code: {language}. Supported languages: {", ".join(SUPPORTED_LANGUAGES.keys())}'
        }), 400
    
    results = []
    
    for image in images:
        filename = secure_filename(image.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(file_path)
        
        try:
            processed_path = preprocess_image(file_path, language)
            img = Image.open(processed_path)
            text = pytesseract.image_to_string(img, lang=language)
            
            results.append({
                'filename': filename,
                'extracted_text': text
            })
            
        except Exception as e:
            results.append({
                'filename': filename,
                'error': str(e)
            })
            
        finally:
            # Dọn dẹp file tạm thời
            if os.path.exists(file_path):
                os.remove(file_path)
            
            processed_path = file_path + "_processed.jpg"
            if os.path.exists(processed_path):
                os.remove(processed_path)
    
    return jsonify({
        'results': results,
        'language': language,
        'language_name': SUPPORTED_LANGUAGES[language]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
