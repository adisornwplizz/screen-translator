#!/usr/bin/env python3
"""
Demo script for vocabulary table functionality
แสดงตัวอย่างการทำงานของระบบตารางคำศัพท์
"""

import sys
import os

# เพิ่ม path สำหรับ import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def demo_vocabulary_extraction():
    """แสดงตัวอย่างการทำงานของระบบคำศัพท์"""
    print("📚 Demo: ระบบตารางคำศัพท์ Screen Translator")
    print("=" * 60)
    
    try:
        from translation.vocabulary import VocabularyManager
        
        # สร้าง mock translator สำหรับ demo
        class MockTranslator:
            def __init__(self):
                # สร้างพจนานุกรมง่าย ๆ สำหรับ demo
                self.dictionary = {
                    'computer': 'คอมพิวเตอร์',
                    'programming': 'การเขียนโปรแกรม',
                    'technology': 'เทคโนโลยี',
                    'software': 'ซอฟต์แวร์',
                    'hardware': 'ฮาร์ดแวร์',
                    'database': 'ฐานข้อมูล',
                    'network': 'เครือข่าย',
                    'security': 'ความปลอดภัย',
                    'algorithm': 'อัลกอริทึม',
                    'development': 'การพัฒนา',
                    'application': 'แอปพลิเคชัน',
                    'interface': 'ส่วนติดต่อ',
                    'system': 'ระบบ',
                    'data': 'ข้อมูล',
                    'user': 'ผู้ใช้',
                    'server': 'เซิร์ฟเวอร์',
                    'client': 'ไคลเอนต์',
                    'browser': 'เบราว์เซอร์',
                    'internet': 'อินเทอร์เน็ต',
                    'website': 'เว็บไซต์'
                }
                
            def is_available(self):
                return True
                
            def translate(self, text, target_language='th'):
                # จำลองการแปล
                translation = self.dictionary.get(text.lower(), f'แปล_{text}')
                return {
                    'translated_text': translation,
                    'detected_language': 'en',
                    'confidence': 0.95
                }
        
        # สร้าง VocabularyManager พร้อม mock translator
        translator = MockTranslator()
        vocab_manager = VocabularyManager(translator=translator)
        
        print("📝 กำลังประมวลผลข้อความตัวอย่างจากการ OCR...")
        print()
        
        # ตัวอย่างข้อความที่อาจได้จาก OCR
        sample_texts = [
            "Computer programming is the process of creating software applications.",
            "Database management systems store and organize data efficiently.",
            "Network security protects computer systems from cyber attacks.",
            "Algorithm development requires logical thinking and problem solving.",
            "User interface design affects the overall user experience.",
            "Server hardware must be reliable for continuous operation.",
            "Web browsers connect users to internet websites and applications."
        ]
        
        # ประมวลผลข้อความทีละข้อความ
        for i, text in enumerate(sample_texts, 1):
            print(f"🔍 ข้อความที่ {i}: {text}")
            vocab_manager.process_text(text, f"screen_capture_{i}")
            
            # แสดงคำศัพท์ใหม่ที่พบ
            current_vocab = vocab_manager.get_vocabulary_for_display()
            if current_vocab:
                print(f"   📖 พบคำศัพท์ใหม่: {len([v for v in current_vocab if 'แปล_' not in v[1]])} คำ")
            print()
        
        # แสดงตารางคำศัพท์ทั้งหมด
        print("📊 ตารางคำศัพท์ที่รวบรวมได้:")
        print("-" * 60)
        vocabulary_data = vocab_manager.get_vocabulary_for_display()
        
        # แสดงในรูปแบบตาราง
        print(f"{'Vocabulary':<15} | {'Meaning':<25}")
        print("-" * 45)
        
        for word, meaning in vocabulary_data:
            # จำกัดความยาวสำหรับการแสดงผล
            word_display = word[:14] if len(word) > 14 else word
            meaning_display = meaning[:24] if len(meaning) > 24 else meaning
            print(f"{word_display:<15} | {meaning_display:<25}")
        
        # แสดงสถิติ
        stats = vocab_manager.get_statistics()
        print("-" * 45)
        print(f"📈 สถิติ:")
        print(f"   • คำศัพท์ทั้งหมด: {stats['total_words']} คำ")
        print(f"   • แปลเสร็จแล้ว: {stats['words_with_meaning']} คำ")
        print(f"   • ความครบถ้วน: {stats['completion_rate']:.1f}%")
        
        print("\n✨ คุณสมบัติของระบบตารางคำศัพท์:")
        print("   • สกัดคำศัพท์อัตโนมัติจากข้อความที่ OCR จับได้")
        print("   • กรองคำทั่วไปที่ไม่จำเป็น (the, a, an, etc.)")
        print("   • แปลความหมายอัตโนมัติด้วยระบบแปลภาษา")
        print("   • นับความถี่การใช้งานของแต่ละคำ")
        print("   • แสดงผลในรูปแบบตารางที่อ่านง่าย")
        print("   • สถิติความคืบหน้าการแปล")
        
        print("\n🎯 ประโยชน์สำหรับผู้ใช้:")
        print("   • ทบทวนคำศัพท์ใหม่ที่พบในเนื้อหา")
        print("   • เรียนรู้คำศัพท์เฉพาะทาง")
        print("   • สร้างพจนานุกรมส่วนตัว")
        print("   • ติดตามความก้าวหน้าในการเรียนรู้")
        
        return True
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการ demo: {e}")
        return False

def main():
    """เรียกใช้ demo"""
    success = demo_vocabulary_extraction()
    
    if success:
        print("\n🎉 Demo เสร็จสิ้น! ระบบตารางคำศัพท์พร้อมใช้งาน")
        return 0
    else:
        print("\n❌ Demo ไม่สำเร็จ")
        return 1

if __name__ == "__main__":
    sys.exit(main())