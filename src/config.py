# การตั้งค่าระบบ Screen Translator

# การตั้งค่า OCR
OCR_CONFIG = {
    'tesseract_cmd': r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # เปลี่ยนตามที่ติดตั้ง
    'language': 'eng',  # ภาษาไทยและอังกฤษ
    'config': '--psm 6'  # Page Segmentation Mode
}

# การตั้งค่าการแปล
TRANSLATION_CONFIG = {
    'source_language': 'auto',
    'target_language': 'th',  # แปลเป็นภาษาไทย
    'service': 'google',
    'enable_cache': True,  # เปิดใช้งาน cache เพื่อหลีกเลี่ยงการแปลข้อความซ้ำ
    'cache_size': 100  # จำนวนคำแปลที่เก็บใน cache
}

# การตั้งค่า UI
UI_CONFIG = {
    'update_interval': 1000,  # milliseconds
    'capture_interval': 2000,  # milliseconds - ระยะเวลาในการจับข้อความ
    'capture_interval_min': 500,  # milliseconds - ค่าต่ำสุด
    'capture_interval_max': 10000,  # milliseconds - ค่าสูงสุด
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

# การตั้งค่า Ollama Models
OLLAMA_CONFIG = {
    'host': 'localhost',
    'port': 11434,
    'vision_model': 'gemma3:4b',  # Model สำหรับ AI Vision (OCR)
    'translation_model': 'gemma3:4b',  # Model สำหรับการแปล
    'custom_prompt': '',  # Custom prompt สำหรับการแปล (เปล่า = ใช้ default)
    'default_prompt': """For the following English text, please go through each sentence and paragraph to enhance its readability and naturalness, making it sound like it was originally written by a native English speaker. Pay attention to sentence structure, vocabulary, and common expressions. Once the English version is optimized, please provide a comprehensive and accurate Thai translation.

English text:
{text}

Respond ONLY with the final Thai translation sentence. Do not include any English, explanations, or extra formatting."""
}

# Legacy settings (เก็บไว้เพื่อความเข้ากันได้)
API_KEY = "your_translation_api_key_here"
OCR_API_URL = "https://api.ocr-service.com/recognize"
TRANSLATION_API_URL = "https://api.translation-service.com/translate"
SCREEN_REGION = (100, 100, 800, 600)
LANGUAGE_FROM = "en"
LANGUAGE_TO = "th"