"""
Ollama Translator Module for Screen Translator
ใช้ Ollama API เพื่อแปลภาษาอังกฤษเป็นไทยด้วย Gemma 3:4b model
"""

import requests
import json
import time
import re
from typing import Dict, List, Optional


class OllamaTranslator:
    """Translator ที่ใช้ Ollama API กับ Gemma 3:4b model"""
    
    def __init__(self, host: str = "localhost", port: int = 11434, model: str = "gemma3:4b"):
        """
        เริ่มต้น Ollama Translator
        
        Args:
            host (str): Ollama server host
            port (int): Ollama server port
            model (str): Model name ที่จะใช้
        """
        self.host = host
        self.port = port
        self.model = model
        self.base_url = f"http://{host}:{port}"
        self.api_url = f"{self.base_url}/api/generate"
        self.session = requests.Session()
        
        # กำหนด timeout
        self.timeout = 30
        
        # ตรวจสอบการเชื่อมต่อ
        self.is_connected = self._test_connection()
        
        if self.is_connected:
            print(f"✅ เชื่อมต่อ Ollama สำเร็จ - Model: {self.model}")
        else:
            print(f"❌ ไม่สามารถเชื่อมต่อ Ollama ได้ - {self.base_url}")

    def _test_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อกับ Ollama"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                # ตรวจสอบว่ามี model ที่ต้องการหรือไม่
                models = response.json().get('models', [])
                model_names = [model.get('name', '') for model in models]
                if any(self.model in name for name in model_names):
                    return True
                else:
                    print(f"⚠️ Model {self.model} ไม่พบในระบบ")
                    print(f"📋 Models ที่มี: {', '.join(model_names)}")
                    return False
            return False
        except Exception as e:
            print(f"❌ ข้อผิดพลาดในการทดสอบการเชื่อมต่อ: {e}")
            return False

    def _detect_language(self, text: str) -> str:
        """ตรวจจับภาษาอย่างง่าย"""
        # ตรวจจับอักขระไทย
        thai_pattern = re.compile(r'[\u0E00-\u0E7F]')
        if thai_pattern.search(text):
            return 'th'
        
        # ตรวจจับอักขระอังกฤษ
        english_pattern = re.compile(r'[a-zA-Z]')
        if english_pattern.search(text):
            return 'en'
        
        return 'unknown'

    def _create_prompt(self, text: str) -> str:
        """สร้าง prompt สำหรับ Ollama - ปรับปรุงให้เข้าใจก่อนแล้วค่อยสรุป"""
        prompt = f"""You are a professional English to Thai translator. Follow these steps:

STEP 1: Understand the English text completely
- Identify the main message and context
- Recognize any technical terms, idioms, or cultural references
- Consider the appropriate tone and formality level

STEP 2: Translate to natural Thai
- Use clear, natural Thai language that Thai speakers would actually use
- Choose appropriate Thai vocabulary that matches the context
- Maintain the original meaning and tone
- For technical terms, use commonly accepted Thai equivalents or keep English terms when appropriate

Rules:
- ONLY translate from English to Thai
- If input is already Thai or other languages, return unchanged
- Return ONLY the final Thai translation, no explanations or steps
- Use appropriate Thai punctuation and formatting

English text: "{text}"

Thai translation:"""
        
        return prompt

    def translate(self, text: str, target_language: str = 'th', source_language: str = 'auto') -> Dict:
        """
        แปลข้อความจากอังกฤษเป็นไทย
        
        Args:
            text (str): ข้อความที่จะแปล
            target_language (str): ภาษาเป้าหมาย (รองรับเฉพาะ 'th')
            source_language (str): ภาษาต้นฉบับ
            
        Returns:
            dict: ผลลัพธ์การแปล
        """
        if not text or not text.strip():
            return {
                'translated_text': '',
                'detected_language': 'unknown',
                'confidence': 0.0,
                'service': 'ollama'
            }
        
        # ตรวจสอบการเชื่อมต่อ
        if not self.is_connected:
            return {
                'translated_text': text,
                'detected_language': 'error',
                'confidence': 0.0,
                'service': 'ollama',
                'error': 'Ollama not connected'
            }
        
        # จำกัดให้แปลเป็นภาษาไทยเท่านั้น
        if target_language != 'th':
            return {
                'translated_text': text,
                'detected_language': 'unsupported',
                'confidence': 0.0,
                'service': 'ollama',
                'error': f'Target language {target_language} not supported'
            }
        
        # ตรวจจับภาษาต้นฉบับ
        detected_lang = self._detect_language(text)
        
        # ถ้าเป็นภาษาไทยอยู่แล้ว ไม่ต้องแปล
        if detected_lang == 'th':
            return {
                'translated_text': text,
                'detected_language': 'th',
                'confidence': 1.0,
                'service': 'ollama'
            }
        
        # ถ้าไม่ใช่ภาษาอังกฤษ ไม่แปล
        if detected_lang != 'en':
            return {
                'translated_text': text,
                'detected_language': detected_lang,
                'confidence': 0.0,
                'service': 'ollama',
                'error': 'Only English to Thai translation supported'
            }
        
        try:
            # เตรียม prompt
            prompt = self._create_prompt(text)
            
            # เรียก Ollama API
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # ลดความสุ่มเพื่อการแปลที่สอดคล้อง
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            print(f"🔄 กำลังแปลด้วย Ollama ({self.model})...")
            
            response = self.session.post(
                self.api_url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result.get('response', '').strip()
                
                # ทำความสะอาดผลลัพธ์
                translated_text = self._clean_translation(translated_text)
                
                return {
                    'translated_text': translated_text,
                    'detected_language': 'en',
                    'confidence': 0.9,
                    'service': 'ollama',
                    'model': self.model
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ Ollama API error: {error_msg}")
                return {
                    'translated_text': text,
                    'detected_language': 'error',
                    'confidence': 0.0,
                    'service': 'ollama',
                    'error': error_msg
                }
        
        except requests.exceptions.Timeout:
            print("⏰ Ollama API timeout")
            return {
                'translated_text': text,
                'detected_language': 'error',
                'confidence': 0.0,
                'service': 'ollama',
                'error': 'Request timeout'
            }
        except Exception as e:
            print(f"❌ Ollama translation error: {e}")
            return {
                'translated_text': text,
                'detected_language': 'error',
                'confidence': 0.0,
                'service': 'ollama',
                'error': str(e)
            }

    def _clean_translation(self, text: str) -> str:
        """ทำความสะอาดผลลัพธ์การแปล"""
        # ลบข้อความที่ไม่จำเป็นที่ model อาจจะเพิ่มเข้ามา
        unwanted_phrases = [
            "Thai translation:",
            "ความหมาย:",
            "แปลเป็นไทย:",
            "คำแปล:",
            "ผลลัพธ์:",
        ]
        
        for phrase in unwanted_phrases:
            text = text.replace(phrase, "").strip()
        
        # ลบเครื่องหมาย quotes ที่ไม่จำเป็น
        text = text.strip('"\'')
        
        return text.strip()

    def batch_translate(self, texts: List[str], target_language: str = 'th') -> List[Dict]:
        """
        แปลข้อความหลายๆ ข้อความ
        
        Args:
            texts (list): รายการข้อความที่จะแปล
            target_language (str): ภาษาเป้าหมาย
            
        Returns:
            list: รายการผลลัพธ์การแปล
        """
        results = []
        
        for i, text in enumerate(texts):
            print(f"🔄 แปลข้อความ {i+1}/{len(texts)}")
            result = self.translate(text, target_language)
            results.append(result)
            
            # หน่วงเวลาเล็กน้อยเพื่อไม่ให้ Ollama ติดขัด
            if i < len(texts) - 1:
                time.sleep(0.5)
        
        return results

    def test_translation(self):
        """ทดสอบการแปลด้วย Ollama"""
        test_texts = [
            "Hello World!",
            "How are you today?",
            "This is a screen translator application.",
            "Please select the area you want to translate.",
            "The weather is nice today.",
            "สวัสดีครับ",  # ภาษาไทยอยู่แล้ว
            "こんにちは",     # ภาษาญี่ปุ่น (ไม่รองรับ)
        ]
        
        print("🧪 ทดสอบการแปลด้วย Ollama:")
        print("=" * 60)
        
        for text in test_texts:
            print(f"📝 ข้อความต้นฉบับ: {text}")
            
            result = self.translate(text)
            
            print(f"🔍 ภาษาที่ตรวจพบ: {result['detected_language']}")
            print(f"🔄 ผลลัพธ์: {result['translated_text']}")
            print(f"⚡ Service: {result['service']}")
            
            if 'error' in result:
                print(f"❌ ข้อผิดพลาด: {result['error']}")
            
            print("─" * 60)

    def is_available(self) -> bool:
        """ตรวจสอบว่า Ollama พร้อมใช้งานหรือไม่"""
        return self.is_connected
    
    def get_model_info(self) -> Dict:
        """ข้อมูล model ที่ใช้"""
        return {
            'service': 'ollama',
            'model': self.model,
            'host': self.host,
            'port': self.port,
            'available': self.is_available(),
            'supported_languages': {
                'source': ['en'],
                'target': ['th']
            }
        }


if __name__ == "__main__":
    # ทดสอบ Ollama Translator
    translator = OllamaTranslator()
    
    if translator.is_available():
        translator.test_translation()
    else:
        print("❌ Ollama ไม่พร้อมใช้งาน กรุณาตรวจสอบ:")
        print("   1. Ollama กำลังทำงาน")
        print("   2. Ollama ทำงานบน port 11434")
        print("   3. Model gemma3:4b ได้ถูก pull แล้ว")
        print("   4. สั่งรัน: ollama pull gemma3:4b")
