import cv2
import numpy as np
from PIL import Image
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import CAPTURE_CONFIG
import base64
import requests
from io import BytesIO
from .ollama_translator import OllamaTranslator


class OCR:
    def __init__(self, vision_model='gemma3:4b'):
        """เริ่มต้น OCR engine ด้วย Ollama Vision
        vision_model: model ที่ใช้สำหรับ Ollama Vision
        """
        self.vision_model = vision_model
        try:
            self.ollama = OllamaTranslator(model=self.vision_model)
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการตั้งค่า OCR: {e}")
    
    def update_vision_model(self, model: str):
        """อัปเดต vision model สำหรับ Ollama Vision"""
        self.vision_model = model
        self.ollama = OllamaTranslator(model=self.vision_model)
        print(f"🔄 เปลี่ยน vision model เป็น: {self.vision_model}")

    def capture_screen(self, region):
        """จับภาพหน้าจอในพื้นที่ที่กำหนด
        
        Args:
            region (tuple): (x, y, width, height)
            
        Returns:
            PIL.Image: ภาพที่จับได้
        """
        import pyautogui
        
        try:
            x, y, width, height = region
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            return screenshot
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการจับภาพ: {e}")
            return None

    def process_image(self, image):
        """ประมวลผลภาพเพื่อเพิ่มความชัดเจนสำหรับ OCR
        
        Args:
            image (PIL.Image): ภาพต้นฉบับ
            
        Returns:
            PIL.Image: ภาพที่ประมวลผลแล้ว
        """
        try:
            if image is None:
                return None
                
            # จำกัดขนาดภาพสูงสุดเพื่อป้องกันการใช้ทรัพยากรมากเกินไป
            MAX_WIDTH, MAX_HEIGHT = 1920, 1080
            if image.width > MAX_WIDTH or image.height > MAX_HEIGHT:
                # ปรับขนาดภาพโดยคงอัตราส่วน
                ratio = min(MAX_WIDTH / image.width, MAX_HEIGHT / image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                print(f"🔄 ปรับขนาดภาพเป็น {new_size} เพื่อประหยัดทรัพยากร")
                
            # แปลงเป็น numpy array
            img_array = np.array(image)
            
            # แปลงเป็น grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # เพิ่มความคมชัด (Contrast Enhancement)
            if CAPTURE_CONFIG['image_processing']['contrast_enhancement']:
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                gray = clahe.apply(gray)
            
            # ลดสัญญาณรบกวน (Noise Reduction) - ปรับค่าให้ประหยัดทรัพยากรมากขึ้น
            if CAPTURE_CONFIG['image_processing']['noise_reduction']:
                gray = cv2.bilateralFilter(gray, 5, 50, 50)
            
            # เพิ่มความคมชัด (Sharpening) - ใช้ kernel เบาลง
            if CAPTURE_CONFIG['image_processing']['sharpening']:
                kernel = np.array([[0, -1, 0],
                                  [-1, 5, -1],
                                  [0, -1, 0]])
                gray = cv2.filter2D(gray, -1, kernel)
            
            # ปรับค่า threshold
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # แปลงกลับเป็น PIL Image
            processed_image = Image.fromarray(binary)
            
            # บันทึกภาพ debug (ถ้าต้องการ)
            if CAPTURE_CONFIG['save_debug_images']:
                self._save_debug_image(processed_image, "processed")
            
            return processed_image
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการประมวลผลภาพ: {e}")
            return image

    def extract_text_ollama_vision(self, image):
        """ใช้ Ollama Vision อ่านข้อความจากภาพ"""
        try:
            # แปลงภาพเป็น base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode()
            prompt = "Read all text in this image. Return only the text, no explanation."
            payload = {
                "model": self.vision_model,
                "prompt": prompt,
                "images": [img_b64],
                "stream": False,
                "options": {"temperature": 0.1, "max_tokens": 1024}
            }
            url = f"http://localhost:11434/api/generate"
            # ลดเวลา timeout เพื่อป้องกันการค้าง - จาก 60 วินาที เป็น 15 วินาที
            # เพิ่ม connection timeout เพื่อจัดการปัญหาเครือข่าย
            response = requests.post(url, json=payload, timeout=(5, 15))  # (connect_timeout, read_timeout)
            if response.status_code == 200:
                result = response.json()
                text = result.get('response', '').strip()
                return text
            else:
                print(f"❌ Ollama Vision error: {response.text}")
                return ""
        except requests.exceptions.ConnectTimeout:
            print(f"❌ Ollama Vision connection timeout: ไม่สามารถเชื่อมต่อ Ollama ได้")
            return ""
        except requests.exceptions.ReadTimeout:
            print(f"❌ Ollama Vision read timeout: Ollama ตอบสนองช้าเกินไป")
            return ""
        except requests.exceptions.RequestException as e:
            print(f"❌ Ollama Vision network error: {e}")
            return ""
        except Exception as e:
            print(f"❌ Ollama Vision OCR error: {e}")
            return ""

    def extract_text(self, image):
        """สกัดข้อความจากภาพด้วย Ollama Vision"""
        return self.extract_text_ollama_vision(image)

    def get_text_with_confidence(self, image):
        """สกัดข้อความพร้อมค่าความมั่นใจ สำหรับ Ollama Vision"""
        text = self.extract_text_ollama_vision(image)
        # AI Vision ไม่มี confidence score ที่แท้จริง ให้คืน 0.9 ถ้ามีข้อความ, 0 ถ้าไม่มี
        conf = 0.9 if text.strip() else 0.0
        return text, conf

    def _clean_text(self, text):
        """ทำความสะอาดข้อความ
        
        Args:
            text (str): ข้อความดิบ
            
        Returns:
            str: ข้อความที่ทำความสะอาดแล้ว
        """
        if not text:
            return ""
        
        # ลบบรรทัดที่ว่าง
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # รวมบรรทัด
        cleaned = ' '.join(lines)
        
        # ลบช่องว่างซ้ำ
        cleaned = ' '.join(cleaned.split())
        
        return cleaned

    def _save_debug_image(self, image, suffix):
        """บันทึกภาพสำหรับ debug
        
        Args:
            image (PIL.Image): ภาพที่จะบันทึก
            suffix (str): ส่วนท้ายของชื่อไฟล์
        """
        try:
            debug_folder = CAPTURE_CONFIG['debug_folder']
            if not os.path.exists(debug_folder):
                os.makedirs(debug_folder)
            
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"debug_{suffix}_{timestamp}.png"
            filepath = os.path.join(debug_folder, filename)
            
            image.save(filepath)
            print(f"💾 บันทึกภาพ debug: {filepath}")
            
        except Exception as e:
            print(f"❌ ไม่สามารถบันทึกภาพ debug: {e}")

    def test_ocr(self):
        """ทดสอบการทำงานของ OCR"""
        try:
            # สร้างภาพทดสอบ
            from PIL import Image, ImageDraw, ImageFont
            
            img = Image.new('RGB', (400, 200), color='white')
            draw = ImageDraw.Draw(img)
            
            # เขียนข้อความทดสอบ
            test_text = "Hello World!\nสวัสดีครับ"
            draw.text((50, 50), test_text, fill='black')
            
            # ทดสอบ OCR
            result = self.extract_text(img)
            confidence = self.get_text_with_confidence(img)[1]
            
            print(f"🧪 ทดสอบ OCR:")
            print(f"   ข้อความต้นฉบับ: {test_text}")
            print(f"   ผลลัพธ์ OCR: {result}")
            print(f"   ความมั่นใจ: {confidence:.1f}%")
            
            return result, confidence
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการทดสอบ OCR: {e}")
            return "", 0