# Image to Text Converter

This project is a simple image to text converter using Python, Pillow, and Tesseract OCR.

## Requirements
- Python 3.x
- Pillow
- pytesseract
- Tesseract OCR (must be installed separately)

## Installation
1. Clone the repository or download the files.
2. Navigate to the project directory.
3. (Optional) Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Install Tesseract OCR:
   ```bash
   brew install tesseract  # For macOS users
   ```

## Usage
Run the script using:
```bash
python image_to_text.py
```
Enter the path to the image file when prompted, and the extracted text will be displayed in the console. 