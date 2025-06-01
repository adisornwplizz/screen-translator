"""
Utils module - Organized helper functions for screen translator application
"""

import os
import sys
import json
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import pyautogui


# =============================================================================
# IMAGE PROCESSING FUNCTIONS
# =============================================================================

def resize_image(image, size):
    """ปรับขนาดภาพ"""
    return image.resize(size, Image.Resampling.LANCZOS)


def crop_image_safely(image, x, y, width, height):
    """ครอบตัดภาพอย่างปลอดภัย"""
    try:
        # ตรวจสอบขอบเขต
        img_width, img_height = image.size
        
        # ปรับขอบเขตให้อยู่ในภาพ
        left = max(0, min(x, img_width))
        top = max(0, min(y, img_height))
        right = max(left, min(x + width, img_width))
        bottom = max(top, min(y + height, img_height))
        
        # ครอบตัด
        if right > left and bottom > top:
            return image.crop((left, top, right, bottom))
        else:
            return None
            
    except Exception as e:
        print(f"❌ ไม่สามารถครอบตัดภาพ: {e}")
        return None


def save_image(image, path):
    """บันทึกภาพ"""
    try:
        # สร้างโฟลเดอร์ถ้าไม่มี
        os.makedirs(os.path.dirname(path), exist_ok=True)
        image.save(path)
        return True
    except Exception as e:
        print(f"❌ ไม่สามารถบันทึกภาพ: {e}")
        return False


def load_image(path):
    """โหลดภาพ"""
    try:
        return Image.open(path)
    except Exception as e:
        print(f"❌ ไม่สามารถโหลดภาพ: {e}")
        return None


def create_test_image(text="Test Text", size=(400, 200)):
    """สร้างภาพทดสอบ"""
    try:
        # สร้างภาพพื้นหลังขาว
        image = Image.new('RGB', size, color='white')
        draw = ImageDraw.Draw(image)
        
        # ใช้ฟอนต์ default
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # คำนวณตำแหน่งข้อความให้อยู่กลาง
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = (size[0] - text_width) // 2
        text_y = (size[1] - text_height) // 2
        
        # วาดข้อความ
        draw.text((text_x, text_y), text, fill='black', font=font)
        
        return image
        
    except Exception as e:
        print(f"❌ ไม่สามารถสร้างภาพทดสอบ: {e}")
        return None


# =============================================================================
# TEXT PROCESSING FUNCTIONS
# =============================================================================

def format_text(text):
    """จัดรูปแบบข้อความ"""
    if not text:
        return ""
    
    # ลบบรรทัดว่างและช่องว่างส่วนเกิน
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    formatted = '\n'.join(lines)
    
    return formatted


def extract_text_from_image(image, engine='tesseract'):
    """Helper สำหรับสกัดข้อความจากภาพด้วย engine ที่เลือก"""
    try:
        if engine == 'tesseract':
            import pytesseract
            return pytesseract.image_to_string(image, lang='tha+eng')
        else:
            print(f"❌ ไม่รู้จัก OCR engine: {engine}")
            return ""
    except Exception as e:
        print(f"❌ ไม่สามารถสกัดข้อความ: {e}")
        return ""


# =============================================================================
# SYSTEM FUNCTIONS
# =============================================================================

def get_screen_size():
    """ได้ขนาดหน้าจอ"""
    return pyautogui.size()


def validate_region(x, y, width, height):
    """ตรวจสอบความถูกต้องของพื้นที่"""
    screen_width, screen_height = get_screen_size()
    
    # ตรวจสอบค่าติดลบ
    if x < 0 or y < 0 or width <= 0 or height <= 0:
        return False
    
    # ตรวจสอบว่าอยู่ในขอบเขตหน้าจอ
    if x + width > screen_width or y + height > screen_height:
        return False
    
    return True


def get_system_info():
    """ได้ข้อมูลระบบ"""
    import platform
    
    info = {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'screen_size': get_screen_size(),
        'app_data_dir': get_app_data_dir()
    }
    
    return info


def check_dependencies():
    """ตรวจสอบ dependencies ที่จำเป็น"""
    dependencies = {
        'PyQt5': 'PyQt5',
        'PIL': 'Pillow',
        'cv2': 'opencv-python',
        'pytesseract': 'pytesseract',
        'googletrans': 'googletrans',
        'pyautogui': 'pyautogui',
        'numpy': 'numpy'
    }
    
    missing = []
    
    for module, package in dependencies.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    return missing


# =============================================================================
# FILE SYSTEM FUNCTIONS
# =============================================================================

def get_app_data_dir():
    """ได้โฟลเดอร์สำหรับเก็บข้อมูลแอป"""
    import platform
    
    system = platform.system()
    if system == "Windows":
        base_dir = os.environ.get('APPDATA')
    elif system == "Darwin":  # macOS
        base_dir = os.path.expanduser("~/Library/Application Support")
    else:  # Linux และ Unix อื่น ๆ
        base_dir = os.path.expanduser("~/.local/share")
    
    app_dir = os.path.join(base_dir, "ScreenTranslator")
    os.makedirs(app_dir, exist_ok=True)
    
    return app_dir


def clean_filename(filename):
    """ทำความสะอาดชื่อไฟล์"""
    import re
    # ลบอักขระที่ไม่ได้รับอนุญาตในชื่อไฟล์
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return cleaned.strip()


def save_settings(settings, file_path):
    """บันทึกการตั้งค่า"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ ไม่สามารถบันทึกการตั้งค่า: {e}")
        return False


def load_settings(file_path, default_settings=None):
    """โหลดการตั้งค่า"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default_settings or {}
    except Exception as e:
        print(f"❌ ไม่สามารถโหลดการตั้งค่า: {e}")
        return default_settings or {}


# =============================================================================
# LOGGING FUNCTIONS
# =============================================================================

def setup_logging(log_file='screen_translator.log', level=logging.INFO):
    """ตั้งค่า logging"""
    log_path = os.path.join(get_app_data_dir(), log_file)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def create_timestamp():
    """สร้าง timestamp สำหรับการบันทึก"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")