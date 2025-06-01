import os
import sys
import json
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import pyautogui


def resize_image(image, size):
    """ปรับขนาดภาพ"""
    return image.resize(size, Image.Resampling.LANCZOS)


def format_text(text):
    """จัดรูปแบบข้อความ"""
    if not text:
        return ""
    
    # ลบบรรทัดว่างและช่องว่างส่วนเกิน
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    formatted = '\n'.join(lines)
    
    return formatted


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


def get_screen_size():
    """ได้ขนาดหน้าจอ"""
    return pyautogui.size()


def create_timestamp():
    """สร้าง timestamp สำหรับการบันทึก"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_settings(settings, file_path):
    """บันทึกการตั้งค่า"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ ไม่สามารถบันทึกการตั้งค่า: {e}")
        return False


def load_settings(file_path, default_settings=None):
    """โหลดการตั้งค่า"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return default_settings or {}
    except Exception as e:
        print(f"❌ ไม่สามารถโหลดการตั้งค่า: {e}")
        return default_settings or {}


def setup_logging(log_file='screen_translator.log', level=logging.INFO):
    """ตั้งค่า logging"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


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


def crop_image_safely(image, x, y, width, height):
    """ครอบตัดภาพอย่างปลอดภัย"""
    try:
        # ตรวจสอบขอบเขต
        img_width, img_height = image.size
        
        # ปรับค่าให้อยู่ในขอบเขต
        x = max(0, min(x, img_width))
        y = max(0, min(y, img_height))
        width = min(width, img_width - x)
        height = min(height, img_height - y)
        
        if width <= 0 or height <= 0:
            return None
            
        return image.crop((x, y, x + width, y + height))
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการครอบตัดภาพ: {e}")
        return None


def create_test_image(text="Test Text", size=(400, 200)):
    """สร้างภาพทดสอบ"""
    try:
        img = Image.new('RGB', size, color='white')
        draw = ImageDraw.Draw(img)
        
        # ใช้ font เริ่มต้น
        try:
            # ลอง font ของ Windows
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            try:
                font = ImageFont.truetype("tahoma.ttf", 20)
            except:
                font = ImageFont.load_default()
        
        # หาตำแหน่งกลาง
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        # วาดข้อความ
        draw.text((x, y), text, fill='black', font=font)
        
        return img
        
    except Exception as e:
        print(f"❌ ไม่สามารถสร้างภาพทดสอบ: {e}")
        return None


def clean_filename(filename):
    """ทำความสะอาดชื่อไฟล์"""
    import re
    # ลบอักขระที่ไม่ได้รับอนุญาต
    cleaned = re.sub(r'[<>:"/\\|?*]', '', filename)
    return cleaned.strip()


def get_app_data_dir():
    """ได้โฟลเดอร์สำหรับเก็บข้อมูลแอป"""
    if sys.platform == "win32":
        app_data = os.environ.get('APPDATA', '')
        app_dir = os.path.join(app_data, 'ScreenTranslator')
    else:
        home = os.path.expanduser('~')
        app_dir = os.path.join(home, '.screen_translator')
    
    os.makedirs(app_dir, exist_ok=True)
    return app_dir


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

def extract_text_from_image(image, engine='tesseract'):
    """Helper สำหรับสกัดข้อความจากภาพด้วย engine ที่เลือก"""
    if engine == 'ollama_vision':
        from translation.ocr import OCR
        ocr = OCR(engine='ollama_vision')
        return ocr.extract_text(image)
    else:
        import pytesseract
        return pytesseract.image_to_string(image)