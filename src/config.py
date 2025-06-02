# การตั้งค่าระบบ Screen Translator

# การตั้งค่าการแปล
TRANSLATION_CONFIG = {
    'source_language': 'auto',
    'target_language': 'th',  # แปลเป็นภาษาไทย
    'service': 'google',
    'enable_cache': False,  # ปิดใช้งาน cache เพื่อประหยัดทรัพยากร
}

# การตั้งค่า UI
UI_CONFIG = {
    'update_interval': 1000,  # milliseconds
    'capture_interval': 5000,  # milliseconds - เพิ่มเป็น 5 วินาทีเพื่อลดความถี่และป้องกันการค้าง
    'capture_interval_min': 2000,  # milliseconds - เพิ่มค่าต่ำสุดเพื่อประหยัดทรัพยากร
    'capture_interval_max': 15000,  # milliseconds - เพิ่มค่าสูงสุด
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