"""
Vocabulary Extraction and Management Module for Screen Translator
จัดการการสกัดและเก็บคำศัพท์จากข้อความที่ระบบตรวจจับได้
"""

import re
import json
import os
from typing import List, Dict, Set, Optional
from collections import defaultdict


class VocabularyExtractor:
    """คลาสสำหรับสกัดและจัดการคำศัพท์"""
    
    def __init__(self):
        """เริ่มต้น Vocabulary Extractor"""
        self.vocabulary_data = {}  # {word: {meaning: str, frequency: int, contexts: List[str]}}
        self.ignored_words = set()  # คำที่ไม่ต้องการเก็บ
        self.min_word_length = 2  # ความยาวขั้นต่ำของคำ
        self.max_vocabulary_size = 1000  # จำนวนคำศัพท์สูงสุดที่เก็บ
        
        # โหลดคำที่ไม่ต้องการเก็บ (common words)
        self._load_ignored_words()
        
    def _load_ignored_words(self):
        """โหลดรายการคำที่ไม่ต้องการเก็บ (เช่น the, a, an, is, are)"""
        # Common English words ที่ไม่จำเป็นต้องเก็บ
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'among', 'around', 'through', 'until', 'since',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
            'can', 'must', 'shall', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
            'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'ours', 'theirs'
        }
        self.ignored_words.update(common_words)
        
    def extract_words(self, text: str) -> List[str]:
        """สกัดคำศัพท์จากข้อความ
        
        Args:
            text (str): ข้อความที่จะสกัดคำศัพท์
            
        Returns:
            List[str]: รายการคำศัพท์ที่สกัดได้
        """
        if not text or not text.strip():
            return []
            
        # ทำความสะอาดข้อความ
        cleaned_text = self._clean_text(text)
        
        # แยกคำออกจากกัน
        words = re.findall(r'\b[a-zA-Z]+\b', cleaned_text)
        
        # กรองคำตามเงื่อนไข
        filtered_words = []
        for word in words:
            word_lower = word.lower()
            if (len(word) >= self.min_word_length and 
                word_lower not in self.ignored_words and
                self._is_valid_word(word)):
                filtered_words.append(word_lower)
                
        return list(set(filtered_words))  # ลบคำซ้ำ
        
    def _clean_text(self, text: str) -> str:
        """ทำความสะอาดข้อความ"""
        # ลบอักขระพิเศษและตัวเลข
        cleaned = re.sub(r'[^\w\s]', ' ', text)
        # ลบช่องว่างซ้ำ
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()
        
    def _is_valid_word(self, word: str) -> bool:
        """ตรวจสอบว่าเป็นคำที่ถูกต้องหรือไม่"""
        # ตรวจสอบว่าไม่ใช่ตัวเลขทั้งหมด
        if word.isdigit():
            return False
            
        # ตรวจสอบว่าไม่ใช่อักขระซ้ำ (เช่น "aaa", "xxx")
        if len(set(word.lower())) == 1:
            return False
            
        return True
        
    def add_vocabulary(self, word: str, meaning: str = "", context: str = ""):
        """เพิ่มคำศัพท์ลงในฐานข้อมูล
        
        Args:
            word (str): คำศัพท์
            meaning (str): ความหมาย
            context (str): บริบทที่พบคำนี้
        """
        word_lower = word.lower()
        
        if word_lower in self.vocabulary_data:
            # อัพเดทข้อมูลที่มีอยู่
            self.vocabulary_data[word_lower]['frequency'] += 1
            if context and context not in self.vocabulary_data[word_lower]['contexts']:
                self.vocabulary_data[word_lower]['contexts'].append(context)
            if meaning and not self.vocabulary_data[word_lower]['meaning']:
                self.vocabulary_data[word_lower]['meaning'] = meaning
        else:
            # เพิ่มคำศัพท์ใหม่
            self.vocabulary_data[word_lower] = {
                'meaning': meaning,
                'frequency': 1,
                'contexts': [context] if context else [],
                'original_word': word  # เก็บรูปแบบเดิมของคำ
            }
            
        # จำกัดขนาดของ vocabulary
        if len(self.vocabulary_data) > self.max_vocabulary_size:
            self._cleanup_vocabulary()
            
    def _cleanup_vocabulary(self):
        """ทำความสะอาด vocabulary โดยลบคำที่ใช้น้อย"""
        # เรียงตาม frequency และลบคำที่ใช้น้อยที่สุด
        sorted_words = sorted(
            self.vocabulary_data.items(),
            key=lambda x: x[1]['frequency']
        )
        
        # ลบ 10% ของคำที่ใช้น้อยที่สุด
        remove_count = max(1, len(sorted_words) // 10)
        for word, _ in sorted_words[:remove_count]:
            del self.vocabulary_data[word]
            
    def get_vocabulary_list(self) -> List[Dict]:
        """ได้รายการคำศัพท์ทั้งหมด
        
        Returns:
            List[Dict]: รายการคำศัพท์ [{'word': str, 'meaning': str, 'frequency': int}]
        """
        vocabulary_list = []
        for word, data in self.vocabulary_data.items():
            vocabulary_list.append({
                'word': data.get('original_word', word),
                'meaning': data.get('meaning', ''),
                'frequency': data.get('frequency', 0),
                'contexts': data.get('contexts', [])
            })
            
        # เรียงตาม frequency จากมากไปน้อย
        vocabulary_list.sort(key=lambda x: x['frequency'], reverse=True)
        return vocabulary_list
        
    def get_vocabulary_for_table(self) -> List[List[str]]:
        """ได้ข้อมูลคำศัพท์สำหรับแสดงในตาราง
        
        Returns:
            List[List[str]]: [['word1', 'meaning1'], ['word2', 'meaning2'], ...]
        """
        vocabulary_list = self.get_vocabulary_list()
        table_data = []
        
        for vocab in vocabulary_list:
            word = vocab['word']
            meaning = vocab['meaning'] if vocab['meaning'] else 'กำลังแปล...'
            table_data.append([word, meaning])
            
        return table_data
        
    def has_word(self, word: str) -> bool:
        """ตรวจสอบว่ามีคำศัพท์นี้อยู่แล้วหรือไม่"""
        return word.lower() in self.vocabulary_data
        
    def get_word_meaning(self, word: str) -> str:
        """ได้ความหมายของคำศัพท์"""
        word_lower = word.lower()
        if word_lower in self.vocabulary_data:
            return self.vocabulary_data[word_lower].get('meaning', '')
        return ''
        
    def update_word_meaning(self, word: str, meaning: str):
        """อัพเดทความหมายของคำศัพท์"""
        word_lower = word.lower()
        if word_lower in self.vocabulary_data:
            self.vocabulary_data[word_lower]['meaning'] = meaning
            
    def clear_vocabulary(self):
        """ล้างคำศัพท์ทั้งหมด"""
        self.vocabulary_data.clear()
        
    def get_vocabulary_count(self) -> int:
        """ได้จำนวนคำศัพท์ทั้งหมด"""
        return len(self.vocabulary_data)
        
    def save_vocabulary(self, filepath: str):
        """บันทึกคำศัพท์ลงไฟล์
        
        Args:
            filepath (str): path ของไฟล์ที่จะบันทึก
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.vocabulary_data, f, ensure_ascii=False, indent=2)
            print(f"✅ บันทึกคำศัพท์ไปยัง {filepath}")
        except Exception as e:
            print(f"❌ ไม่สามารถบันทึกคำศัพท์: {e}")
            
    def load_vocabulary(self, filepath: str):
        """โหลดคำศัพท์จากไฟล์
        
        Args:
            filepath (str): path ของไฟล์ที่จะโหลด
        """
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.vocabulary_data = json.load(f)
                print(f"✅ โหลดคำศัพท์จาก {filepath} ({len(self.vocabulary_data)} คำ)")
            else:
                print(f"⚠️ ไม่พบไฟล์คำศัพท์: {filepath}")
        except Exception as e:
            print(f"❌ ไม่สามารถโหลดคำศัพท์: {e}")


class VocabularyManager:
    """คลาสสำหรับจัดการคำศัพท์แบบครบวงจร"""
    
    def __init__(self, translator=None):
        """เริ่มต้น Vocabulary Manager
        
        Args:
            translator: ตัวแปลภาษา (Translator instance)
        """
        self.extractor = VocabularyExtractor()
        self.translator = translator
        self.auto_translate = True  # แปลอัตโนมัติ
        
    def process_text(self, text: str, context: str = ""):
        """ประมวลผลข้อความและสกัดคำศัพท์
        
        Args:
            text (str): ข้อความที่จะประมวลผล
            context (str): บริบทของข้อความ
        """
        # สกัดคำศัพท์
        words = self.extractor.extract_words(text)
        
        # เพิ่มคำศัพท์ลงในฐานข้อมูล
        for word in words:
            if not self.extractor.has_word(word):
                # คำใหม่ - เพิ่มลงฐานข้อมูลและแปลถ้าต้องการ
                meaning = ""
                if self.auto_translate and self.translator:
                    meaning = self._translate_word(word)
                    
                self.extractor.add_vocabulary(word, meaning, context)
            else:
                # คำที่มีอยู่แล้ว - เพิ่ม frequency และ context
                self.extractor.add_vocabulary(word, "", context)
                
                # แปลถ้ายังไม่มีความหมาย
                if (self.auto_translate and self.translator and 
                    not self.extractor.get_word_meaning(word)):
                    meaning = self._translate_word(word)
                    if meaning:
                        self.extractor.update_word_meaning(word, meaning)
                        
    def _translate_word(self, word: str) -> str:
        """แปลคำศัพท์เดียว
        
        Args:
            word (str): คำที่จะแปล
            
        Returns:
            str: ความหมายที่แปลแล้ว
        """
        try:
            if self.translator and self.translator.is_available():
                result = self.translator.translate(word, target_language='th')
                return result.get('translated_text', '')
        except Exception as e:
            print(f"❌ ไม่สามารถแปลคำ '{word}': {e}")
        return ''
        
    def get_vocabulary_for_display(self) -> List[List[str]]:
        """ได้ข้อมูลคำศัพท์สำหรับแสดงผล"""
        return self.extractor.get_vocabulary_for_table()
        
    def set_translator(self, translator):
        """ตั้งค่าตัวแปลภาษา"""
        self.translator = translator
        
    def set_auto_translate(self, enabled: bool):
        """ตั้งค่าการแปลอัตโนมัติ"""
        self.auto_translate = enabled
        
    def clear_all(self):
        """ล้างคำศัพท์ทั้งหมด"""
        self.extractor.clear_vocabulary()
        
    def get_statistics(self) -> Dict:
        """ได้สถิติของคำศัพท์"""
        vocabulary_list = self.extractor.get_vocabulary_list()
        total_words = len(vocabulary_list)
        words_with_meaning = sum(1 for vocab in vocabulary_list if vocab['meaning'])
        
        return {
            'total_words': total_words,
            'words_with_meaning': words_with_meaning,
            'completion_rate': (words_with_meaning / total_words * 100) if total_words > 0 else 0
        }