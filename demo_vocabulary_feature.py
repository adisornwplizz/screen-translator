#!/usr/bin/env python3
"""
Vocabulary Table Feature Demo
This script demonstrates the new vocabulary table functionality
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demo_vocabulary_table():
    """Demonstrate the vocabulary table feature"""
    
    print("🎯 Screen Translator - Vocabulary Table Feature Demo")
    print("=" * 60)
    print("✨ เพิ่ม Feature: ตารางแสดงคำศัพท์ (Vocabulary Table)")
    print("=" * 60)
    
    from utils.vocabulary import extract_vocabulary_from_text
    
    print("\n📋 Feature Overview:")
    print("• ตารางสรุปคำศัพท์พร้อมความหมายที่ดึงมาจากเนื้อหา")
    print("• ช่วยให้ผู้ใช้เรียนรู้และทบทวนคำศัพท์ใหม่ได้อย่างมีประสิทธิภาพ")
    print("• แสดงผลด้านล่างของกล่องคำแปล")
    print("• คอลัมน์: Vocabulary (คำศัพท์) | Meaning (ความหมาย)")
    
    print("\n🎭 Demo Scenarios:")
    
    scenarios = [
        {
            'title': '🍽️  Restaurant Menu (English)',
            'text': 'Welcome to our restaurant! Today special includes grilled salmon with vegetables.',
            'description': 'สถานการณ์: อ่านเมนูร้านอาหาร'
        },
        {
            'title': '🏥  Hospital Sign (Thai)',
            'text': 'สวัสดี ยินดีต้อนรับ โรงพยาบาล แผนกฉุกเฉิน ห้องตรวจ',
            'description': 'สถานการณ์: อ่านป้ายโรงพยาบาล'
        },
        {
            'title': '💻  Software Interface (Mixed)',
            'text': 'Configuration settings ตั้งค่า Database ฐานข้อมูล Password รหัสผ่าน',
            'description': 'สถานการณ์: อ่านหน้าจอซอฟต์แวร์'
        },
        {
            'title': '🗞️  News Article (English)',
            'text': 'Breaking news: Scientists discover revolutionary medical treatment for patients.',
            'description': 'สถานการณ์: อ่านข่าวออนไลน์'
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{scenario['title']}")
        print(f"📝 {scenario['description']}")
        print(f"🔤 Text: \"{scenario['text']}\"")
        
        # Extract vocabulary
        vocabulary = extract_vocabulary_from_text(scenario['text'], 'auto', max_count=6)
        
        if vocabulary:
            print(f"📚 Vocabulary Table ({len(vocabulary)} words):")
            print("┌─" + "─"*18 + "┬─" + "─"*30 + "┐")
            print("│ Vocabulary       │ Meaning (in app)             │")
            print("├─" + "─"*18 + "┼─" + "─"*30 + "┤")
            
            # Mock translations for demo
            mock_translations = {
                'Welcome': 'ยินดีต้อนรับ',
                'Restaurant': 'ร้านอาหาร',
                'Today': 'วันนี้',
                'Special': 'พิเศษ',
                'Includes': 'รวม',
                'Grilled': 'ย่าง',
                'Salmon': 'ปลาแซลมอน',
                'Vegetables': 'ผัก',
                'Breaking': 'ด่วน',
                'News': 'ข่าว',
                'Scientists': 'นักวิทยาศาสตร์',
                'Discover': 'ค้นพบ',
                'Revolutionary': 'ปฏิวัติ',
                'Medical': 'การแพทย์',
                'Treatment': 'การรักษา',
                'Patients': 'ผู้ป่วย',
                'Configuration': 'การตั้งค่า',
                'Settings': 'การตั้งค่า',
                'Database': 'ฐานข้อมูล',
                'Password': 'รหัสผ่าน'
            }
            
            for word in vocabulary:
                meaning = mock_translations.get(word, f"แปล: {word}")
                print(f"│ {word:<16} │ {meaning:<28} │")
            
            print("└─" + "─"*18 + "┴─" + "─"*30 + "┘")
        else:
            print("📚 No vocabulary extracted")
    
    print("\n🎯 Key Benefits:")
    print("✅ ทบทวนคำศัพท์ใหม่ได้สะดวก")
    print("✅ เรียนรู้คำศัพท์จากบริบทจริง")
    print("✅ แสดงผลแบบตารางที่อ่านง่าย")
    print("✅ รองรับทั้งภาษาไทยและอังกฤษ")
    print("✅ อัปเดตอัตโนมัติตามเนื้อหาที่แปล")
    
    print("\n🔧 Technical Features:")
    print("• Smart word extraction with stop-word filtering")
    print("• Language-specific processing (Thai/English/Mixed)")
    print("• Professional UI with proper table styling")
    print("• Error handling and empty state management")
    print("• Performance optimized vocabulary translation")
    
    print("\n✨ Implementation Complete!")
    print("🚀 Ready for production use!")

if __name__ == "__main__":
    demo_vocabulary_table()