#!/usr/bin/env python3
"""
Demo script สำหรับทดสอบ Screen Translator พร้อม Ollama integration
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QTextEdit, QHBoxLayout, QGroupBox

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.window import Window
from translation.translator import Translator
from translation.ollama_translator import OllamaTranslator

class OllamaDemoWindow(QMainWindow):
    """หน้าต่างสำหรับทดสอบ Ollama integration"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Translator - Ollama Demo")
        self.setGeometry(100, 100, 800, 600)
        
        # สร้าง UI
        self.setup_ui()
        
        # ทดสอบ Ollama
        self.test_ollama_connection()
    
    def setup_ui(self):
        """สร้าง UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # ข้อมูลการใช้งาน
        info_label = QLabel("""
🚀 Screen Translator with Ollama Integration

✨ ฟีเจอร์ใหม่:
• ใช้ Ollama API กับ Gemma 2:4b model สำหรับแปลภาษา
• จำกัดการแปลเฉพาะ English → Thai เท่านั้น  
• รันบน Docker port 11434
• Fallback ไปใช้ Google Translate หาก Ollama ไม่พร้อมใช้งาน

🔧 การตั้งค่า Ollama:
• ตรวจสอบว่า Docker engine ทำงานอยู่
• Ollama container ต้องทำงานบน port 11434
• Model gemma2:4b ต้องถูก pull แล้ว
        """)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }")
        layout.addWidget(info_label)
        
        # ปุ่มควบคุม
        button_layout = QHBoxLayout()
        
        self.main_app_button = QPushButton("🎯 เปิด Screen Translator หลัก")
        self.main_app_button.clicked.connect(self.open_main_app)
        self.main_app_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(self.main_app_button)
        
        self.test_button = QPushButton("🧪 ทดสอบ Ollama")
        self.test_button.clicked.connect(self.test_ollama_translation)
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        button_layout.addWidget(self.test_button)
        
        layout.addLayout(button_layout)
        
        # ผลลัพธ์การทดสอบ
        result_group = QGroupBox("ผลลัพธ์การทดสอบ")
        result_layout = QVBoxLayout(result_group)
        
        self.result_text = QTextEdit()
        self.result_text.setFont(self.font())
        self.result_text.setMaximumHeight(300)
        result_layout.addWidget(self.result_text)
        
        layout.addWidget(result_group)
        
        # ตัวแปรสำหรับ main app
        self.main_window = None
    
    def test_ollama_connection(self):
        """ทดสอบการเชื่อมต่อ Ollama เบื้องต้น"""
        self.result_text.append("🔍 ตรวจสอบการเชื่อมต่อ Ollama...")
        
        try:
            import requests
            
            # ทดสอบการเชื่อมต่อ
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                self.result_text.append(f"✅ เชื่อมต่อ Ollama สำเร็จ")
                self.result_text.append(f"📋 พบ {len(models)} models:")
                
                gemma_found = False
                for model in models:
                    name = model.get('name', 'unknown')
                    size = model.get('size', 0)
                    size_gb = size // (1024*1024*1024) if size > 0 else 0
                    self.result_text.append(f"   • {name} ({size_gb:.1f}GB)")
                      if 'gemma3' in name and '4b' in name:
                        gemma_found = True
                        self.result_text.append(f"   ✅ พบ {name} พร้อมใช้งาน!")
                
                if not gemma_found:
                    self.result_text.append("⚠️ ไม่พบ gemma3:4b model")
                    self.result_text.append("💡 รัน: ollama pull gemma2:4b")
                    
            else:
                self.result_text.append(f"❌ HTTP {response.status_code}: ไม่สามารถเชื่อมต่อ Ollama")
                
        except requests.exceptions.ConnectionError:
            self.result_text.append("❌ ไม่สามารถเชื่อมต่อ Ollama")
            self.result_text.append("💡 ตรวจสอบ:")
            self.result_text.append("   • Docker engine ทำงานหรือไม่")
            self.result_text.append("   • Ollama container บน port 11434")
        except Exception as e:
            self.result_text.append(f"❌ ข้อผิดพลาด: {e}")
        
        self.result_text.append("─" * 50)
    
    def test_ollama_translation(self):
        """ทดสอบการแปลด้วย Ollama"""
        self.result_text.append("🧪 ทดสอบการแปลด้วย Ollama...")
        
        try:
            # สร้าง Ollama translator
            ollama = OllamaTranslator()
            
            if ollama.is_available():
                self.result_text.append("✅ Ollama พร้อมใช้งาน")
                
                # ทดสอบการแปล
                test_texts = [
                    "Hello World!",
                    "How are you today?",
                    "This is a screen translator application.",
                    "Good morning, have a nice day!"
                ]
                
                for text in test_texts:
                    self.result_text.append(f"\n📝 ข้อความ: {text}")
                    result = ollama.translate(text)
                    
                    if 'error' not in result:
                        self.result_text.append(f"🔄 แปลเป็น: {result['translated_text']}")
                        self.result_text.append(f"⚡ Service: {result.get('service', 'unknown')}")
                    else:
                        self.result_text.append(f"❌ ข้อผิดพลาด: {result['error']}")
            else:
                self.result_text.append("❌ Ollama ไม่พร้อมใช้งาน")
                
        except Exception as e:
            self.result_text.append(f"❌ เกิดข้อผิดพลาด: {e}")
            import traceback
            self.result_text.append(traceback.format_exc())
        
        self.result_text.append("─" * 50)
    
    def open_main_app(self):
        """เปิด Screen Translator หลัก"""
        if self.main_window is None:
            self.main_window = Window(title="Screen Translator with Ollama")
        
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
        
        # อัปเดตสถานะใน main app
        service_info = self.main_window.translator.get_service_info()
        status_text = f"สถานะ: ใช้ {service_info['service']} - "
        status_text += "พร้อมใช้งาน" if service_info['available'] else "ไม่พร้อมใช้งาน"
        self.main_window.status_label.setText(status_text)
        
        self.result_text.append("🚀 เปิด Screen Translator หลักแล้ว")

def main():
    app = QApplication(sys.argv)
    
    print("🚀 Screen Translator with Ollama Integration")
    print("=" * 60)
    
    # สร้างหน้าต่างสำหรับเลือก
    demo_window = OllamaDemoWindow()
    demo_window.show()
    
    print("✅ Demo window แสดงแล้ว")
    print("💡 เลือก:")
    print("   • ทดสอบ Ollama connection")
    print("   • เปิด Screen Translator หลัก")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
