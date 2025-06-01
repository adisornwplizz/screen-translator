"""
Vocabulary extraction and processing utilities for Screen Translator
"""
import re
import string
from typing import List, Dict, Tuple


class VocabularyExtractor:
    """คลาสสำหรับสกัดคำศัพท์จากข้อความ"""
    
    def __init__(self):
        # คำที่ไม่ควรแสดงในตารางคำศัพท์ (stop words)
        self.english_stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their'
        }
        
        self.thai_stop_words = {
            'และ', 'หรือ', 'แต่', 'ใน', 'บน', 'ที่', 'เพื่อ', 'ของ', 'กับ', 'โดย',
            'เป็น', 'คือ', 'มี', 'มีา', 'ได้', 'จะ', 'ก็', 'ไป', 'มา', 'อยู่',
            'นี้', 'นั้น', 'เหล่านี้', 'เหล่านั้น', 'ฉัน', 'คุณ', 'เขา', 'เธอ',
            'มัน', 'เรา', 'พวกเขา', 'ผม', 'ดิฉัน', 'ของฉัน', 'ของคุณ', 'ของเขา'
        }
    
    def extract_vocabulary(self, text: str, source_language: str = 'auto') -> List[str]:
        """
        สกัดคำศัพท์จากข้อความ
        
        Args:
            text (str): ข้อความที่จะสกัดคำศัพท์
            source_language (str): ภาษาต้นฉบับ ('en', 'th', 'auto')
            
        Returns:
            List[str]: รายการคำศัพท์ที่สกัดได้
        """
        if not text or not text.strip():
            return []
        
        # ทำความสะอาดข้อความ
        cleaned_text = self._clean_text(text)
        
        # แยกคำศัพท์ตามภาษา
        if source_language == 'th' or self._is_thai_text(cleaned_text):
            return self._extract_thai_vocabulary(cleaned_text)
        elif source_language == 'en' or self._is_english_text(cleaned_text):
            return self._extract_english_vocabulary(cleaned_text)
        else:
            # auto detect: ลองทั้งสองภาษา
            return self._extract_mixed_vocabulary(cleaned_text)
    
    def _clean_text(self, text: str) -> str:
        """ทำความสะอาดข้อความ"""
        # ลบอักขระพิเศษบางตัว แต่เก็บไว้สำหรับการแยกคำ
        text = re.sub(r'[^\w\s\u0E00-\u0E7F.-]', ' ', text)
        # ลบช่องว่างซ้ำ
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _is_thai_text(self, text: str) -> bool:
        """ตรวจสอบว่าเป็นข้อความไทยหรือไม่"""
        thai_chars = len(re.findall(r'[\u0E00-\u0E7F]', text))
        total_chars = len(re.findall(r'[^\s]', text))
        return total_chars > 0 and (thai_chars / total_chars) > 0.3
    
    def _is_english_text(self, text: str) -> bool:
        """ตรวจสอบว่าเป็นข้อความอังกฤษหรือไม่"""
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(re.findall(r'[^\s]', text))
        return total_chars > 0 and (english_chars / total_chars) > 0.5
    
    def _extract_thai_vocabulary(self, text: str) -> List[str]:
        """สกัดคำศัพท์ไทย"""
        # สำหรับภาษาไทย: แยกตามช่องว่างและอักขระพิเศษ
        words = re.findall(r'[\u0E00-\u0E7F]+', text)
        
        # กรองคำที่มีความยาวเหมาะสม
        filtered_words = []
        for word in words:
            word = word.strip()
            if (len(word) >= 2 and  # ยาวอย่างน้อย 2 ตัวอักษร
                word.lower() not in self.thai_stop_words and
                not word.isdigit()):  # ไม่ใช่ตัวเลข
                filtered_words.append(word)
        
        # ลบคำซ้ำแต่คงลำดับ
        return list(dict.fromkeys(filtered_words))
    
    def _extract_english_vocabulary(self, text: str) -> List[str]:
        """สกัดคำศัพท์อังกฤษ"""
        # แยกคำอังกฤษ
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        
        # กรองคำที่มีความยาวเหมาะสม
        filtered_words = []
        for word in words:
            word = word.strip().lower()
            if (len(word) >= 3 and  # ยาวอย่างน้อย 3 ตัวอักษร
                word not in self.english_stop_words and
                not word.isdigit() and  # ไม่ใช่ตัวเลข
                word.isalpha()):  # เป็นตัวอักษรเท่านั้น
                # เก็บรูปแบบ title case
                filtered_words.append(word.capitalize())
        
        # ลบคำซ้ำแต่คงลำดับ
        return list(dict.fromkeys(filtered_words))
    
    def _extract_mixed_vocabulary(self, text: str) -> List[str]:
        """สกัดคำศัพท์จากข้อความผสม"""
        vocabulary = []
        
        # สกัดคำไทย
        thai_words = self._extract_thai_vocabulary(text)
        vocabulary.extend(thai_words)
        
        # สกัดคำอังกฤษ
        english_words = self._extract_english_vocabulary(text)
        vocabulary.extend(english_words)
        
        return vocabulary
    
    def filter_vocabulary_by_length(self, vocabulary: List[str], min_length: int = 2, max_length: int = 20) -> List[str]:
        """กรองคำศัพท์ตามความยาว"""
        return [word for word in vocabulary if min_length <= len(word) <= max_length]
    
    def limit_vocabulary_count(self, vocabulary: List[str], max_count: int = 10) -> List[str]:
        """จำกัดจำนวนคำศัพท์"""
        return vocabulary[:max_count]


def extract_vocabulary_from_text(text: str, source_language: str = 'auto', max_count: int = 10) -> List[str]:
    """
    ฟังก์ชันหลักสำหรับสกัดคำศัพท์จากข้อความ
    
    Args:
        text (str): ข้อความต้นฉบับ
        source_language (str): ภาษาต้นฉบับ
        max_count (int): จำนวนคำศัพท์สูงสุด
        
    Returns:
        List[str]: รายการคำศัพท์
    """
    extractor = VocabularyExtractor()
    vocabulary = extractor.extract_vocabulary(text, source_language)
    vocabulary = extractor.filter_vocabulary_by_length(vocabulary)
    vocabulary = extractor.limit_vocabulary_count(vocabulary, max_count)
    return vocabulary