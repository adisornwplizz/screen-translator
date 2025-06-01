#!/usr/bin/env python3
"""
Demo script สำหรับทดสอบ SelectionWidget ที่ปรับปรุงแล้ว
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gui.window import SelectionWidget

class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Translator - Selection Demo")
        self.setGeometry(100, 100, 400, 200)
        
        # สร้าง SelectionWidget
        self.selection_widget = SelectionWidget()
        self.selection_widget.position_changed.connect(self.on_selection_changed)
        
        # สร้าง UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # ข้อมูลการใช้งาน
        info_label = QLabel("""
🎯 การทดสอบ Selection Widget ที่ปรับปรุงแล้ว

✨ ฟีเจอร์ใหม่:
• ลากปรับขนาดได้จากทุกมุม (8 จุด)
• ลากขอบเพื่อปรับขนาดในทิศทางเดียว  
• Cursor เปลี่ยนตามตำแหน่งที่เลื่อน
• แสดงข้อมูลขนาดแบบ real-time
• จำกัดขนาดขั้นต่ำ (50x50 pixels)

🆕 ฟีเจอร์ที่เพิ่มใหม่:
• 🖱️ Click-Through: คลิกนอกกรอบจะผ่านไป app ข้างล่าง
• 👁️ Toggle Visibility: กด V เพื่อซ่อน/แสดงกรอบ
• ⌨️ Keyboard Shortcuts: V หรือ Ctrl+V

🖱️ วิธีใช้:
• คลิกปุ่มด้านล่างเพื่อแสดงกรอบเลือกพื้นที่
• ลากตรงกลางเพื่อย้ายตำแหน่ง
• ลากมุมหรือขอบเพื่อปรับขนาด
• กด V เพื่อซ่อน/แสดงกรอบ
• คลิกนอกกรอบเพื่อทดสอบ click-through
• กด ESC เพื่อปิดกรอบ
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # ปุ่มแสดง selection
        self.show_button = QPushButton("📐 แสดงกรอบเลือกพื้นที่")
        self.show_button.clicked.connect(self.show_selection)
        self.show_button.setStyleSheet("""
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
        layout.addWidget(self.show_button)
        
        # ปุ่ม toggle visibility
        self.toggle_button = QPushButton("👁️ Toggle Visibility")
        self.toggle_button.clicked.connect(self.toggle_visibility)
        self.toggle_button.setToolTip("ซ่อน/แสดงกรอบ (กด V)")
        self.toggle_button.setStyleSheet("""
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
        layout.addWidget(self.toggle_button)
        
        # ข้อมูลตำแหน่งและขนาด
        self.position_label = QLabel("ตำแหน่ง: X=100, Y=100, กว้าง=300, สูง=200")
        self.position_label.setStyleSheet("QLabel { font-weight: bold; padding: 8px; }")
        layout.addWidget(self.position_label)
        
        # สถานะการมองเห็น
        self.visibility_label = QLabel("สถานะ: กรอบแสดงอยู่")
        self.visibility_label.setStyleSheet("QLabel { color: #4CAF50; font-weight: bold; padding: 8px; }")
        layout.addWidget(self.visibility_label)
        
    def show_selection(self):
        """แสดงกรอบเลือกพื้นที่"""
        self.selection_widget.show()
        self.selection_widget.raise_()
        self.selection_widget.activateWindow()
        
    def toggle_visibility(self):
        """Toggle การแสดงผลกรอบ"""
        self.selection_widget.toggle_visibility()
        is_visible = self.selection_widget.is_visible_mode()
        status = "แสดงอยู่" if is_visible else "ซ่อนอยู่"
        color = "#4CAF50" if is_visible else "#FF9800"
        self.visibility_label.setText(f"สถานะ: กรอบ{status}")
        self.visibility_label.setStyleSheet(f"QLabel {{ color: {color}; font-weight: bold; padding: 8px; }}")
    
    def on_selection_changed(self, x, y, width, height):
        """อัปเดตข้อมูลเมื่อกรอบเปลี่ยน"""
        self.position_label.setText(f"ตำแหน่ง: X={x}, Y={y}, กว้าง={width}, สูง={height}")
        print(f"📐 Selection changed: ({x}, {y}) - {width}x{height}")
        
    def keyPressEvent(self, event):
        """จัดการ keyboard shortcuts"""
        from PyQt5.QtCore import Qt
        if event.key() == Qt.Key_V:
            self.toggle_visibility()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """ปิดหน้าต่าง selection เมื่อปิดหน้าต่างหลัก"""
        self.selection_widget.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    print("🚀 เริ่มทดสอบ Selection Widget")
    print("=" * 50)
    
    window = DemoWindow()
    window.show()
    
    print("✅ Demo window แสดงแล้ว")
    print("💡 คลิกปุ่มเพื่อทดสอบการปรับขนาดกรอบ")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
