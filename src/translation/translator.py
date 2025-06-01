import os
import sys
from deep_translator import GoogleTranslator
import requests
import time

# เพิ่ม path สำหรับ import config
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import TRANSLATION_CONFIG

# Import OllamaTranslator
try:
    from .ollama_translator import OllamaTranslator
    print("✅ Successfully imported OllamaTranslator from ollama_translator.py")
except ImportError as e:
    print(f"❌ Failed to import OllamaTranslator: {e}")
    # Fallback placeholder
    class OllamaTranslator:
        def __init__(self, *args, **kwargs):
            self.is_connected = False
            print("⚠️ OllamaTranslator fallback placeholder")
        
        def translate(self, text, *args, **kwargs):
            return {
                'translated_text': text,
                'detected_language': 'error',
                'confidence': 0.0,
                'service': 'ollama',
                'error': 'Import issue - using placeholder'
            }
        
        def is_available(self):
            return False


class Translator:
    def __init__(self, service='ollama', ollama_model='gemma3:4b', custom_prompt=''):
        """เริ่มต้น Translator
        
        Args:
            service (str): บริการแปลที่จะใช้ ('google', 'ollama')
            ollama_model (str): Model ที่ใช้สำหรับ Ollama
            custom_prompt (str): Custom prompt สำหรับ Ollama
        """
        self.service = service
        self.google_translator = None
        self.ollama_translator = None
        self.api_key = None
        self.ollama_model = ollama_model
        self.custom_prompt = custom_prompt
        
        # เริ่มต้น service ที่เลือก
        if service == 'ollama':
            try:
                self.ollama_translator = OllamaTranslator(model=ollama_model, custom_prompt=custom_prompt)
                if self.ollama_translator.is_available():
                    print("✅ เชื่อมต่อ Ollama สำเร็จ")
                else:
                    print("❌ ไม่สามารถเชื่อมต่อ Ollama ได้ กลับไปใช้ Google Translate")
                    self.service = 'google'
                    self._init_google_translator()
            except Exception as e:
                print(f"❌ ไม่สามารถเชื่อมต่อ Ollama: {e}")
                print("🔄 กลับไปใช้ Google Translate")
                self.service = 'google'
                self._init_google_translator()
        
        elif service == 'google':
            self._init_google_translator()
        
        # ภาษาที่รองรับ
        if self.service == 'ollama':
            self.supported_languages = {
                'auto': 'ตรวจจับอัตโนมัติ',
                'en': 'อังกฤษ',
                'th': 'ไทย'
            }
        else:
            self.supported_languages = {
                'auto': 'ตรวจจับอัตโนมัติ',
                'th': 'ไทย',
                'en': 'อังกฤษ',
                'ja': 'ญี่ปุ่น',
                'ko': 'เกาหลี',
                'zh': 'จีน',
                'zh-tw': 'จีนแบบดั้งเดิม',
                'fr': 'ฝรั่งเศส',
                'de': 'เยอรมัน',
                'es': 'สเปน',
                'it': 'อิตาลี',
                'ru': 'รัสเซีย',
                'ar': 'อาหรับ',
                'hi': 'ฮินดี',
                'pt': 'โปรตุเกส',
                'vi': 'เวียดนาม',
                'id': 'อินโดนีเซีย',
                'ms': 'มาเลย์',
                'tl': 'ตากาล็อก'
            }
    
    def _init_google_translator(self):
        """เริ่มต้น Google Translator"""
        try:
            self.google_translator = GoogleTranslator(source='auto', target='th')
            print("✅ เชื่อมต่อ Google Translate สำเร็จ")
        except Exception as e:
            print(f"❌ ไม่สามารถเชื่อมต่อ Google Translate: {e}")

    def translate(self, text, target_language='th', source_language='auto'):
        """แปลข้อความ
        
        Args:
            text (str): ข้อความที่จะแปล
            target_language (str): ภาษาเป้าหมาย
            source_language (str): ภาษาต้นฉบับ
            
        Returns:
            dict: ผลลัพธ์การแปล {'translated_text': str, 'detected_language': str, 'confidence': float}
        """
        if not text or not text.strip():
            return {
                'translated_text': '',
                'detected_language': 'unknown',
                'confidence': 0.0
            }
        
        try:
            if self.service == 'ollama' and self.ollama_translator:
                return self.ollama_translator.translate(text, target_language, source_language)
            elif self.service == 'google' and self.google_translator:
                return self._translate_google(text, target_language, source_language)
            else:
                return {
                    'translated_text': text,
                    'detected_language': 'unknown',
                    'confidence': 0.0
                }
                
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการแปล: {e}")
            return {
                'translated_text': text,
                'detected_language': 'error',
                'confidence': 0.0
            }

    def _translate_google(self, text, target_language, source_language):
        """แปลด้วย Google Translate
        
        Args:
            text (str): ข้อความที่จะแปล
            target_language (str): ภาษาเป้าหมาย
            source_language (str): ภาษาต้นฉบับ
            
        Returns:
            dict: ผลลัพธ์การแปล
        """
        try:
            # ตรวจจับภาษาอัตโนมัติด้วย deep-translator
            if source_language == 'auto':
                from deep_translator import single_detection
                detected_lang = single_detection(text, api_key=None)
                confidence = 0.9  # default confidence
            else:
                detected_lang = source_language
                confidence = 1.0
            
            # แปลข้อความ
            if detected_lang == target_language:
                # ไม่ต้องแปลถ้าเป็นภาษาเดียวกัน
                translated_text = text
            else:
                translator = GoogleTranslator(source=detected_lang, target=target_language)
                translated_text = translator.translate(text)
            
            return {
                'translated_text': translated_text,
                'detected_language': detected_lang,
                'confidence': confidence
            }
            
        except Exception as e:
            print(f"❌ Google Translate error: {e}")
            raise e

    def get_supported_languages(self):
        """ได้รายการภาษาที่รองรับ
        
        Returns:
            dict: รายการภาษาที่รองรับ
        """
        return self.supported_languages

    def detect_language(self, text):
        """ตรวจจับภาษาของข้อความ
        
        Args:
            text (str): ข้อความที่จะตรวจจับ
            
        Returns:
            dict: ข้อมูลภาษา {'language': str, 'confidence': float, 'language_name': str}
        """
        try:
            if self.service == 'ollama' and self.ollama_translator:
                # ใช้การตรวจจับภาษาง่าย ๆ สำหรับ Ollama
                import re
                thai_pattern = re.compile(r'[\u0E00-\u0E7F]')
                english_pattern = re.compile(r'[a-zA-Z]')
                
                if thai_pattern.search(text):
                    detected_lang = 'th'
                elif english_pattern.search(text):
                    detected_lang = 'en'
                else:
                    detected_lang = 'unknown'
                
                language_name = self.supported_languages.get(detected_lang, detected_lang)
                
                return {
                    'language': detected_lang,
                    'confidence': 0.9,
                    'language_name': language_name
                }
                
            elif self.service == 'google' and self.google_translator:
                from deep_translator import single_detection
                detected_lang = single_detection(text, api_key=None)
                language_name = self.supported_languages.get(detected_lang, detected_lang)
                
                return {
                    'language': detected_lang,
                    'confidence': 0.9,  # default confidence for deep-translator
                    'language_name': language_name
                }
            else:
                return {
                    'language': 'unknown',
                    'confidence': 0.0,
                    'language_name': 'ไม่ทราบ'
                }
                
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการตรวจจับภาษา: {e}")
            return {
                'language': 'error',
                'confidence': 0.0,
                'language_name': 'ข้อผิดพลาด'
            }

    def batch_translate(self, texts, target_language='th', source_language='auto'):
        """แปลข้อความหลายๆ ข้อความ
        
        Args:
            texts (list): รายการข้อความที่จะแปล
            target_language (str): ภาษาเป้าหมาย
            source_language (str): ภาษาต้นฉบับ
            
        Returns:
            list: รายการผลลัพธ์การแปล
        """
        results = []
        
        for text in texts:
            try:
                result = self.translate(text, target_language, source_language)
                results.append(result)
                
                # หน่วงเวลาเล็กน้อยเพื่อไม่ให้เกิน rate limit
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในการแปลข้อความ: {text[:50]}... - {e}")
                results.append({
                    'translated_text': text,
                    'detected_language': 'error',
                    'confidence': 0.0
                })
        
        return results

    def test_translation(self):
        """ทดสอบการทำงานของ translator"""
        test_texts = [
            "Hello World!",
            "สวัสดีครับ",
            "こんにちは",
            "안녕하세요",
            "你好"
        ]
        
        print("🧪 ทดสอบการแปล:")
        
        for text in test_texts:
            try:
                # ตรวจจับภาษา
                detection = self.detect_language(text)
                print(f"📝 ข้อความ: {text}")
                print(f"🔍 ภาษาที่ตรวจพบ: {detection['language_name']} ({detection['confidence']:.2f})")
                
                # แปลเป็นภาษาไทย
                translation = self.translate(text, 'th')
                print(f"🔄 แปลเป็นไทย: {translation['translated_text']}")
                print("─" * 40)
                
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาด: {e}")

    def is_available(self):
        """ตรวจสอบว่า translator พร้อมใช้งานหรือไม่
        
        Returns:
            bool: True หากพร้อมใช้งาน
        """
        if self.service == 'ollama':
            return self.ollama_translator is not None and self.ollama_translator.is_available()
        elif self.service == 'google':
            return self.google_translator is not None
        return False
    
    def get_service_info(self):
        """ข้อมูลเกี่ยวกับ service ที่ใช้อยู่"""
        if self.service == 'ollama' and self.ollama_translator:
            return self.ollama_translator.get_model_info()
        elif self.service == 'google':
            return {
                'service': 'google',
                'model': 'Google Translate API',
                'available': self.is_available(),
                'supported_languages': self.supported_languages
            }
        else:
            return {
                'service': 'none',
                'model': 'No translator available',
                'available': False,
                'supported_languages': {}
            }
    
    def switch_service(self, new_service):
        """เปลี่ยน translation service
        
        Args:
            new_service (str): Service ใหม่ ('ollama', 'google')
        """
        if new_service == self.service:
            print(f"🔄 กำลังใช้ {new_service} อยู่แล้ว")
            return
        
        print(f"🔄 เปลี่ยนจาก {self.service} เป็น {new_service}")
        
        old_service = self.service
        self.service = new_service
        
        if new_service == 'ollama':
            try:
                if not self.ollama_translator:
                    self.ollama_translator = OllamaTranslator()
                
                if self.ollama_translator.is_available():
                    print("✅ เปลี่ยนเป็น Ollama สำเร็จ")
                    self._update_supported_languages()
                else:
                    print("❌ ไม่สามารถใช้ Ollama ได้ กลับไปใช้ service เดิม")
                    self.service = old_service
            except Exception as e:
                print(f"❌ ข้อผิดพลาดในการเปลี่ยนเป็น Ollama: {e}")
                self.service = old_service
                
        elif new_service == 'google':
            try:
                if not self.google_translator:
                    self._init_google_translator()
                
                if self.google_translator:
                    print("✅ เปลี่ยนเป็น Google Translate สำเร็จ")
                    self._update_supported_languages()
                else:
                    print("❌ ไม่สามารถใช้ Google Translate ได้ กลับไปใช้ service เดิม")
                    self.service = old_service
            except Exception as e:
                print(f"❌ ข้อผิดพลาดในการเปลี่ยนเป็น Google Translate: {e}")
                self.service = old_service
    
    def _update_supported_languages(self):
        """อัปเดตรายการภาษาที่รองรับตาม service ปัจจุบัน"""
        if self.service == 'ollama':
            self.supported_languages = {
                'auto': 'ตรวจจับอัตโนมัติ',
                'en': 'อังกฤษ',
                'th': 'ไทย'
            }
        else:
            self.supported_languages = {
                'auto': 'ตรวจจับอัตโนมัติ',
                'th': 'ไทย',
                'en': 'อังกฤษ',
                'ja': 'ญี่ปุ่น',
                'ko': 'เกาหลี',
                'zh': 'จีน',
                'zh-tw': 'จีนแบบดั้งเดิม',
                'fr': 'ฝรั่งเศส',
                'de': 'เยอรมัน',
                'es': 'สเปน',
                'it': 'อิตาลี',
                'ru': 'รัสเซีย',
                'ar': 'อาหรับ',
                'hi': 'ฮินดี',
                'pt': 'โปรตุเกส',
                'vi': 'เวียดนาม',
                'id': 'อินโดนีเซีย',
                'ms': 'มาเลย์',
                'tl': 'ตากาล็อก'
            }