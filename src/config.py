# การตั้งค่าระบบ Screen Translator

# การตั้งค่า OCR
OCR_CONFIG = {
    'tesseract_cmd': r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # เปลี่ยนตามที่ติดตั้ง
    'language': 'tha+eng',  # ภาษาไทยและอังกฤษ
    'config': '--psm 6'  # Page Segmentation Mode
}

# การตั้งค่าการแปล
TRANSLATION_CONFIG = {
    'source_language': 'auto',
    'target_language': 'th',  # แปลเป็นภาษาไทย
    'service': 'google'
}

# การตั้งค่า UI
UI_CONFIG = {
    'update_interval': 1000,  # milliseconds
    'default_selection_size': (300, 200),
    'min_selection_size': (50, 50),
    'selection_color': (255, 0, 0),  # สีแดง
    'background_opacity': 25,  # ลดความเข้มของพื้นหลัง
    'selection_background': (255, 255, 255, 25)  # สีขาวโปร่งใสอ่อน
}

# การตั้งค่าการจับภาพ
CAPTURE_CONFIG = {
    'image_processing': {
        'contrast_enhancement': True,
        'noise_reduction': True,
        'sharpening': True
    },
    'save_debug_images': False,  # สำหรับ debug
    'debug_folder': 'debug_images'
}

# Legacy settings (เก็บไว้เพื่อความเข้ากันได้)
API_KEY = "your_translation_api_key_here"
OCR_API_URL = "https://api.ocr-service.com/recognize"
TRANSLATION_API_URL = "https://api.translation-service.com/translate"
SCREEN_REGION = (100, 100, 800, 600)
LANGUAGE_FROM = "en"
LANGUAGE_TO = "th"