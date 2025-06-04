import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                            QFrame, QSplitter, QGroupBox, QProgressBar,
                            QCheckBox, QSpinBox, QSlider, QComboBox, QTabWidget,
                            QScrollArea, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal, QThread, pyqtSlot, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QCursor
from PIL import Image

# เพิ่ม path สำหรับ import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from translation.ocr import OCR
from translation.translator import Translator
from translation.ollama_service import ollama_service
from translation.ollama_translator import OllamaTranslator
from config import UI_CONFIG, OLLAMA_CONFIG
from gui.selection_widget import SelectionWidget


class OCRWorker(QThread):
    """Worker thread สำหรับ OCR เพื่อป้องกานการค้างของ UI"""
    finished = pyqtSignal(str, float)  # text, confidence
    error = pyqtSignal(str)  # error message
    
    def __init__(self, ocr, screenshot):
        super().__init__()
        self.ocr = ocr
        self.screenshot = screenshot
        self._is_cancelled = False
    
    def run(self):
        """รัน OCR ใน background thread"""
        try:
            if self._is_cancelled:
                return
                
            # สกัดข้อความพร้อมค่าความมั่นใจ
            text, confidence = self.ocr.get_text_with_confidence(self.screenshot)
            
            if not self._is_cancelled:
                self.finished.emit(text, confidence)
                
        except Exception as e:
            if not self._is_cancelled:
                self.error.emit(str(e))
    
    def cancel(self):
        """ยกเลิกการประมวลผล"""
        self._is_cancelled = True
        self.quit()
        self.wait(2000)  # รอ 2 วินาทีให้ thread หยุด


class Window(QMainWindow):
    def __init__(self, title="Screen Translator - ใช้งานง่าย"):
        super().__init__()
        self.title = title
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 700, 600)  # ลดขนาดให้เหมาะสมกับ UI ใหม่
        
        # Simple mode by default
        self.simple_mode = True
        self.first_time_user = True
        
        # ✨ Use the enhanced SelectionWidget
        self.selection_widget = SelectionWidget()
        self.selection_widget.position_changed.connect(self.on_selection_changed)
        
        # Rest of initialization...
        self.current_selection = QRect(100, 100, 300, 200)
        self.is_capturing = False
        
        # Ollama configuration
        self.vision_model = OLLAMA_CONFIG['vision_model']
        self.translation_model = OLLAMA_CONFIG['translation_model']
        # Always reset custom_prompt to empty on app restart (as per requirement)
        self.custom_prompt = ""  # Reset to default on restart
        OLLAMA_CONFIG['custom_prompt'] = ""  # Update config too
        
        self.ocr = OCR(vision_model=self.vision_model)
        self.translator = Translator(service='ollama', ollama_model=self.translation_model, custom_prompt=self.custom_prompt)
        self.auto_translate = True
        self.target_language = 'th'
        self.last_detected_text = ""
        
        # OCR Worker thread เพื่อป้องกันการค้าง
        self.ocr_worker = None
        
        # การตั้งค่าระยะเวลาการจับภาพ
        self.capture_interval = UI_CONFIG.get('capture_interval', 2000)  # default 2000ms
        
        self.setup_ui()
        
        # Timer setup
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self.capture_and_process)
        
    def setup_ui(self):
        """ตั้งค่า UI แบบใช้งานง่าย - เน้นความเรียบง่ายและใช้งานง่าย"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Simple, clean styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
                color: #212529;
            }
            QWidget {
                background-color: #f8f9fa;
                color: #212529;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: #f8f9fa;
                color: #495057;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Show welcome message for first-time users
        if self.first_time_user:
            self.show_welcome_message()
        
        # Quick start section for simple mode
        if self.simple_mode:
            self.setup_simple_ui(main_layout)
        else:
            self.setup_advanced_ui(main_layout)
    
    def show_welcome_message(self):
        """แสดงข้อความต้อนรับสำหรับผู้ใช้ใหม่"""
        msg = QMessageBox(self)
        msg.setWindowTitle("ยินดีต้อนรับ!")
        msg.setText("ยินดีต้อนรับสู่ Screen Translator! 🎉")
        msg.setInformativeText("แอปนี้จะช่วยแปลข้อความบนหน้าจอให้คุณแบบอัตโนมัติ\n\n"
                              "เริ่มต้นง่ายๆ ด้วย 3 ขั้นตอน:\n"
                              "1️⃣ เลือกพื้นที่บนหน้าจอ\n"
                              "2️⃣ กดปุ่มเริ่ม\n"
                              "3️⃣ ดูผลการแปล\n\n"
                              "คลิก OK เพื่อเริ่มใช้งาน!")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
        self.first_time_user = False
    
    def setup_simple_ui(self, main_layout):
        """ตั้งค่า UI แบบง่าย เน้นใช้งานง่าย"""
        # Title and mode toggle
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🌟 Screen Translator - โหมดใช้งานง่าย")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #007bff;
                padding: 8px;
            }
        """)
        
        self.mode_toggle_btn = QPushButton("⚙️ โหมดขั้นสูง")
        self.mode_toggle_btn.clicked.connect(self.toggle_mode)
        self.mode_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.mode_toggle_btn)
        main_layout.addLayout(header_layout)
        
        # Step-by-step guide
        guide_group = QGroupBox("📋 วิธีการใช้งาน")
        guide_layout = QVBoxLayout(guide_group)
        
        steps = [
            "1️⃣ คลิก 'เลือกพื้นที่' เพื่อกำหนดบริเวณที่ต้องการแปล",
            "2️⃣ ลากกรอบสีแดงไปยังข้อความที่ต้องการ",
            "3️⃣ กด 'เริ่มแปล' เพื่อเริ่มการทำงาน", 
            "4️⃣ ดูผลการแปลในกล่องด้านล่าง"
        ]
        
        for step in steps:
            step_label = QLabel(step)
            step_label.setStyleSheet("""
                QLabel {
                    padding: 4px 8px;
                    background-color: #e9ecef;
                    border-radius: 4px;
                    margin: 2px 0;
                }
            """)
            guide_layout.addWidget(step_label)
        
        main_layout.addWidget(guide_group)
        
        # Main action buttons (large and prominent)
        action_group = QGroupBox("🎮 การควบคุมหลัก")
        action_layout = QVBoxLayout(action_group)
        
        # Selection button
        self.select_area_btn = QPushButton("📐 เลือกพื้นที่บนหน้าจอ")
        self.select_area_btn.clicked.connect(self.show_selection_area)
        self.select_area_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 15px 25px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        
        # Start/Stop buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("▶️ เริ่มแปล")
        self.start_button.clicked.connect(self.start_capture)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        
        self.stop_button = QPushButton("⏸️ หยุด")
        self.stop_button.clicked.connect(self.stop_capture)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        
        action_layout.addWidget(self.select_area_btn)
        action_layout.addLayout(button_layout)
        main_layout.addWidget(action_group)
        
        # Translation result area (big and prominent)
        result_group = QGroupBox("📄 ผลการแปล")
        result_layout = QVBoxLayout(result_group)
        
        self.translated_text = QTextEdit()
        self.translated_text.setFont(QFont("Segoe UI", 13))
        self.translated_text.setPlaceholderText("ผลการแปลจะแสดงที่นี่...\n\n💡 เคล็ดลับ: คุณสามารถคัดลอกข้อความได้โดยการเลือกและกด Ctrl+C")
        self.translated_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 12px;
                background-color: #ffffff;
                color: #212529;
                font-size: 13px;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border: 2px solid #007bff;
            }
        """)
        self.translated_text.setMinimumHeight(200)
        
        result_layout.addWidget(self.translated_text)
        main_layout.addWidget(result_group, 1)  # Give most space to results
        
        # Simple status bar
        self.status_label = QLabel("📍 สถานะ: พร้อมใช้งาน - เลือกพื้นที่เพื่อเริ่มต้น")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #d4edda;
                color: #155724;
                padding: 8px 12px;
                border-radius: 4px;
                border: 1px solid #c3e6cb;
                font-size: 11px;
            }
        """)
        main_layout.addWidget(self.status_label)
        
        # Position info (simplified)
        self.position_label = QLabel("📐 ตำแหน่งการเลือก: ยังไม่ได้เลือก")
        self.position_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                padding: 4px 8px;
                font-size: 10px;
            }
        """)
        main_layout.addWidget(self.position_label)
        
        # Create dummy combo boxes for Ollama models (hidden in simple mode)
        self.vision_model_combo = QComboBox()
        self.vision_model_combo.hide()
        self.translation_model_combo = QComboBox()
        self.translation_model_combo.hide()
        self.prompt_text = QTextEdit()
        self.prompt_text.hide()
        self.reset_prompt_btn = QPushButton()
        self.reset_prompt_btn.hide()
        
        # Initialize Ollama models even in simple mode
        self.load_ollama_models()
    
    def setup_advanced_ui(self, main_layout):
        """ตั้งค่า UI แบบขั้นสูง (เหมือนเดิม + การปรับปรุง)"""
        # Title and mode toggle
        header_layout = QHBoxLayout()
        
        title_label = QLabel("⚙️ Screen Translator - โหมดขั้นสูง")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #dc3545;
                padding: 8px;
            }
        """)
        
        self.mode_toggle_btn = QPushButton("🌟 โหมดง่าย")
        self.mode_toggle_btn.clicked.connect(self.toggle_mode)
        self.mode_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.mode_toggle_btn)
        main_layout.addLayout(header_layout)
        
        # Use tabs for better organization
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                color: #495057;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #007bff;
                border-bottom: 2px solid #007bff;
            }
        """)
        
        # Main tab
        main_tab = QWidget()
        main_tab_layout = QVBoxLayout(main_tab)
        
        # Translation result area (same as simple mode)
        result_group = QGroupBox("📄 ผลการแปล")
        result_layout = QVBoxLayout(result_group)
        
        self.translated_text = QTextEdit()
        self.translated_text.setFont(QFont("Segoe UI", 12))
        self.translated_text.setPlaceholderText("ผลการแปลจะแสดงที่นี่...")
        self.translated_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 10px;
                background-color: #ffffff;
                color: #212529;
            }
            QTextEdit:focus {
                border: 2px solid #007bff;
            }
        """)
        result_layout.addWidget(self.translated_text)
        main_tab_layout.addWidget(result_group, 1)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("▶️ เริ่ม")
        self.start_button.clicked.connect(self.start_capture)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        
        self.stop_button = QPushButton("⏸️ หยุด")
        self.stop_button.clicked.connect(self.stop_capture)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        
        # Toggle visibility button
        self.toggle_button = QPushButton("👁️ ซ่อน/แสดง")
        self.toggle_button.clicked.connect(self.toggle_selection_visibility)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 10px 20px;
                font-size: 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.toggle_button)
        control_layout.addStretch()
        main_tab_layout.addLayout(control_layout)
        
        tab_widget.addTab(main_tab, "หลัก")
        
        # Settings tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # Scroll area for settings
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Interval settings
        interval_group = QGroupBox("⏱️ การตั้งค่าระยะเวลา")
        interval_layout = QVBoxLayout(interval_group)
        
        interval_label = QLabel("ระยะเวลาจับภาพ (วินาที):")
        
        self.interval_slider = QSlider(Qt.Horizontal)
        self.interval_slider.setMinimum(UI_CONFIG.get('capture_interval_min', 2000) // 1000)
        self.interval_slider.setMaximum(UI_CONFIG.get('capture_interval_max', 15000) // 1000)
        self.interval_slider.setValue(self.capture_interval // 1000)
        self.interval_slider.valueChanged.connect(self.on_interval_changed)
        
        self.interval_value_label = QLabel(f"{self.capture_interval // 1000}s")
        self.interval_value_label.setStyleSheet("QLabel { font-weight: bold; color: #007bff; }")
        
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_slider)
        interval_layout.addWidget(self.interval_value_label)
        
        scroll_layout.addWidget(interval_group)
        
        # Ollama settings (simplified)
        ollama_group = QGroupBox("🤖 การตั้งค่า AI")
        ollama_layout = QVBoxLayout(ollama_group)
        
        vision_label = QLabel("AI Vision Model:")
        self.vision_model_combo = QComboBox()
        self.vision_model_combo.currentTextChanged.connect(self.on_vision_model_changed)
        
        translation_label = QLabel("Translation Model:")
        self.translation_model_combo = QComboBox()
        self.translation_model_combo.currentTextChanged.connect(self.on_translation_model_changed)
        
        ollama_layout.addWidget(vision_label)
        ollama_layout.addWidget(self.vision_model_combo)
        ollama_layout.addWidget(translation_label)
        ollama_layout.addWidget(self.translation_model_combo)
        
        scroll_layout.addWidget(ollama_group)
        
        # Custom prompt (collapsible)
        prompt_group = QGroupBox("📝 Custom Prompt (ขั้นสูง)")
        prompt_layout = QVBoxLayout(prompt_group)
        
        self.prompt_text = QTextEdit()
        self.prompt_text.setMaximumHeight(100)
        self.prompt_text.setPlaceholderText("ใส่ custom prompt หรือเว้นว่างเพื่อใช้ default...")
        self.prompt_text.textChanged.connect(self.on_custom_prompt_changed)
        
        self.reset_prompt_btn = QPushButton("🔄 รีเซ็ต")
        self.reset_prompt_btn.clicked.connect(self.reset_custom_prompt)
        
        prompt_layout.addWidget(self.prompt_text)
        prompt_layout.addWidget(self.reset_prompt_btn)
        
        scroll_layout.addWidget(prompt_group)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        settings_layout.addWidget(scroll_area)
        
        tab_widget.addTab(settings_tab, "การตั้งค่า")
        
        # Status tab
        status_tab = QWidget()
        status_layout = QVBoxLayout(status_tab)
        
        self.position_label = QLabel("ตำแหน่ง: X=100, Y=100, กว้าง=300, สูง=200")
        self.status_label = QLabel("สถานะ: พร้อมใช้งาน")
        
        help_label = QLabel("💡 วิธีการใช้: คลิกและลากบริเวณกรอบเพื่อย้าย | เลื่อนเมาส์เพื่อดูไฮไลท์")
        help_label.setWordWrap(True)
        help_label.setStyleSheet("QLabel { color: #6c757d; font-style: italic; }")
        
        status_layout.addWidget(self.position_label)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(help_label)
        status_layout.addStretch()
        
        tab_widget.addTab(status_tab, "สถานะ")
        
        main_layout.addWidget(tab_widget, 1)
        
        # Load Ollama models
        self.load_ollama_models()
    
    def show_selection_area(self):
        """แสดงกรอบเลือกพื้นที่"""
        self.selection_widget.show()
        self.selection_widget.set_visible_mode(True)
        self.selection_widget.set_simple_mode(self.simple_mode)
        self.selection_widget.set_help_text_visible(self.simple_mode)
        if self.simple_mode:
            self.status_label.setText("📍 สถานะ: ลากกรอบสีแดงไปยังข้อความที่ต้องการแปล")
    
    def toggle_mode(self):
        """สลับระหว่างโหมดง่ายและขั้นสูง"""
        self.simple_mode = not self.simple_mode
        
        # Update selection widget mode
        self.selection_widget.set_simple_mode(self.simple_mode)
        self.selection_widget.set_help_text_visible(self.simple_mode)
        
        # Clear and rebuild UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        if self.simple_mode:
            self.setup_simple_ui(main_layout)
        else:
            self.setup_advanced_ui(main_layout)
        
    def on_selection_changed(self, x, y, width, height):
        """เมื่อพื้นที่ที่เลือกเปลี่ยน"""
        self.current_selection = QRect(x, y, width, height)
        
        if self.simple_mode:
            self.position_label.setText(f"📐 ตำแหน่งการเลือก: X={x}, Y={y}, ขนาด={width}x{height}")
            self.status_label.setText("📍 สถานะ: เลือกพื้นที่เรียบร้อย - กด 'เริ่มแปล' เพื่อเริ่มต้น")
        else:
            self.position_label.setText(f"ตำแหน่ง: X={x}, Y={y}, กว้าง={width}, สูง={height}")
    
    def on_interval_changed(self, value):
        """เมื่อระยะเวลาการจับภาพเปลี่ยน"""
        self.capture_interval = value * 1000  # Convert seconds to milliseconds
        self.interval_value_label.setText(f"{value}s")
        
        # ถ้ากำลังจับภาพอยู่ให้อัปเดต timer
        if self.is_capturing:
            self.capture_timer.stop()
            self.capture_timer.start(self.capture_interval)
            print(f"🔄 อัปเดตระยะเวลาการจับภาพเป็น {value} วินาที")
        
    def start_capture(self):
        """เริ่มการจับภาพ real-time"""
        self.is_capturing = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # เริ่ม timer สำหรับจับภาพด้วยระยะเวลาที่กำหนด
        self.capture_timer.start(self.capture_interval)
        
        if self.simple_mode:
            self.status_label.setText(f"🚀 สถานะ: เริ่มแปลแล้ว! (ตรวจสอบทุก {self.capture_interval//1000} วินาที)")
        else:
            self.status_label.setText(f"สถานะ: เริ่มการจับภาพ (ทุก {self.capture_interval//1000} วินาที)")
        
    def stop_capture(self):
        """หยุดการจับภาพ"""
        self.is_capturing = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # หยุด timer
        self.capture_timer.stop()
        
        if self.simple_mode:
            self.status_label.setText("⏸️ สถานะ: หยุดการแปลแล้ว - กด 'เริ่มแปล' เพื่อเริ่มใหม่")
        else:
            self.status_label.setText("สถานะ: หยุดการจับภาพ")
        
    def capture_and_process(self):
        """จับภาพหน้าจอและประมวลผล OCR"""
        try:
            # ตรวจสอบว่า OCR worker ยังทำงานอยู่หรือไม่
            if self.ocr_worker and self.ocr_worker.isRunning():
                print("⚠️ OCR ยังทำงานอยู่ ข้าม capture ครั้งนี้")
                return
                
            if self.simple_mode:
                self.status_label.setText("📸 สถานะ: กำลังจับภาพ...")
            else:
                self.status_label.setText("สถานะ: กำลังจับภาพ...")
            
            # จับภาพพื้นที่ที่เลือก
            region = (
                self.current_selection.x(),
                self.current_selection.y(),
                self.current_selection.width(),
                self.current_selection.height()
            )
            
            # ใช้ OCR สำหรับสกัดข้อความ
            screenshot = self.ocr.capture_screen(region)
            
            if screenshot:
                # ยกเลิก worker เก่าถ้ามี
                if self.ocr_worker:
                    self.ocr_worker.cancel()
                    
                # สร้าง worker ใหม่
                self.ocr_worker = OCRWorker(self.ocr, screenshot)
                self.ocr_worker.finished.connect(self.on_ocr_finished)
                self.ocr_worker.error.connect(self.on_ocr_error)
                
                # เริ่มประมวลผล OCR ใน background
                if self.simple_mode:
                    self.status_label.setText("🔍 สถานะ: กำลังอ่านข้อความ...")
                else:
                    self.status_label.setText("สถานะ: กำลังอ่านข้อความ...")
                self.ocr_worker.start()
            else:
                if self.simple_mode:
                    self.status_label.setText("❌ สถานะ: ไม่สามารถจับภาพได้ - ลองเลือกพื้นที่ใหม่")
                else:
                    self.status_label.setText("สถานะ: ไม่สามารถจับภาพได้")
                
        except Exception as e:
            self.translated_text.clear()
            self.translated_text.append(f"❌ เกิดข้อผิดพลาด: {str(e)}")
            if self.simple_mode:
                self.status_label.setText("❌ สถานะ: เกิดข้อผิดพลาด - ลองใหม่อีกครั้ง")
            else:
                self.status_label.setText("สถานะ: เกิดข้อผิดพลาด")
    
    @pyqtSlot(str, float)
    def on_ocr_finished(self, text, confidence):
        """เมื่อ OCR เสร็จสิ้น"""
        try:
            if self.simple_mode:
                self.status_label.setText("⚡ สถานะ: กำลังแปลข้อความ...")
            else:
                self.status_label.setText("สถานะ: กำลังประมวลผล...")
            
            # แสดงข้อความ
            if text.strip():
                # ตรวจสอบว่าเป็นข้อความใหม่หรือไม่
                if text != self.last_detected_text:
                    # แปลอัตโนมัติเสมอ
                    if self.auto_translate:
                        self.translate_text(text)
                    
                    self.last_detected_text = text
            
            if self.simple_mode:
                self.status_label.setText("✅ สถานะ: พร้อมใช้งาน - กำลังตรวจหาข้อความ...")
            else:
                self.status_label.setText("สถานะ: พร้อมใช้งาน")
            
        except Exception as e:
            self.on_ocr_error(str(e))
    
    @pyqtSlot(str)
    def on_ocr_error(self, error_message):
        """เมื่อ OCR เกิดข้อผิดพลาด"""
        self.translated_text.clear()
        self.translated_text.append(f"❌ เกิดข้อผิดพลาด OCR: {error_message}")
        if self.simple_mode:
            self.status_label.setText("❌ สถานะ: ไม่สามารถอ่านข้อความได้ - ลองปรับตำแหน่งกรอบ")
        else:
            self.status_label.setText("สถานะ: เกิดข้อผิดพลาด OCR")
    
    def translate_text(self, text):
        """แปลข้อความ"""
        try:
            if self.simple_mode:
                self.status_label.setText("🔄 สถานะ: กำลังแปลข้อความ...")
            else:
                self.status_label.setText("สถานะ: กำลังแปล...")
            
            # ตรวจสอบว่า translator พร้อมใช้งานหรือไม่
            if not self.translator.is_available():
                self.translated_text.clear()
                if self.simple_mode:
                    self.translated_text.append("❌ ระบบแปลภาษาไม่พร้อมใช้งาน\n\n💡 กรุณาตรวจสอบการเชื่อมต่ออินเทอร์เน็ต")
                    self.status_label.setText("❌ สถานะ: ระบบแปลไม่พร้อมใช้งาน")
                else:
                    self.translated_text.append("❌ ระบบแปลภาษาไม่พร้อมใช้งาน")
                    self.status_label.setText("สถานะ: ระบบแปลไม่พร้อมใช้งาน")
                return
            
            # แปลข้อความ
            result = self.translator.translate(text, self.target_language)
            
            if result['translated_text']:
                # Auto clean old content when new text arrives
                self.translated_text.clear()
                
                if self.simple_mode:
                    # แสดงข้อความต้นฉบับและคำแปลในโหมดง่าย
                    self.translated_text.append(f"📝 ข้อความต้นฉบับ:\n{text}\n")
                    self.translated_text.append(f"🔄 คำแปล:\n{result['translated_text']}")
                else:
                    # แสดงเฉพาะคำแปลในโหมดขั้นสูง
                    self.translated_text.append(f"{result['translated_text']}")
                
                # เลื่อนไปที่ข้อความล่าสุด
                self.translated_text.verticalScrollBar().setValue(
                    self.translated_text.verticalScrollBar().maximum()
                )
                
                if self.simple_mode:
                    self.status_label.setText("✅ สถานะ: แปลสำเร็จ! กำลังตรวจหาข้อความใหม่...")
                else:
                    self.status_label.setText("สถานะ: แปลสำเร็จ")
            else:
                self.translated_text.clear()
                if self.simple_mode:
                    self.translated_text.append("❌ ไม่สามารถแปลข้อความได้\n\n💡 ลองปรับตำแหน่งกรอบให้ครอบคลุมข้อความที่ชัดเจนขึ้น")
                    self.status_label.setText("❌ สถานะ: ไม่สามารถแปลได้ - ลองใหม่")
                else:
                    self.translated_text.append("❌ ไม่สามารถแปลข้อความได้")
                    self.status_label.setText("สถานะ: แปลไม่สำเร็จ")
                
        except Exception as e:
            self.translated_text.clear()
            if self.simple_mode:
                self.translated_text.append(f"❌ เกิดข้อผิดพลาดในการแปล\n\n🔧 รายละเอียด: {str(e)}\n\n💡 ลองรีสตาร์ทแอปพลิเคชัน")
                self.status_label.setText("❌ สถานะ: เกิดข้อผิดพลาด - ลองใหม่")
            else:
                self.translated_text.append(f"❌ เกิดข้อผิดพลาดในการแปล: {str(e)}")
                self.status_label.setText("สถานะ: เกิดข้อผิดพลาดในการแปล")
    
    def toggle_selection_visibility(self):
        """สลับการแสดงผลของ selection widget"""
        self.selection_widget.toggle_visibility()
        
    def set_selection_visible(self, visible):
        """ตั้งค่าการแสดงผลของ selection widget"""
        self.selection_widget.set_visible_mode(visible)
    
    def load_ollama_models(self):
        """โหลดรายการ models จาก Ollama และอัปเดต UI"""
        try:
            # ล้างรายการเดิม
            self.vision_model_combo.clear()
            self.translation_model_combo.clear()
            
            if ollama_service.is_available():
                # ดึงรายการ models
                vision_models = ollama_service.get_vision_models()
                text_models = ollama_service.get_text_models()
                
                # เพิ่มลงใน combo boxes
                self.vision_model_combo.addItems(vision_models)
                self.translation_model_combo.addItems(text_models)
                
                # ตั้งค่า current selection
                if self.vision_model in vision_models:
                    self.vision_model_combo.setCurrentText(self.vision_model)
                if self.translation_model in text_models:
                    self.translation_model_combo.setCurrentText(self.translation_model)
                
                print(f"✅ โหลด Ollama models สำเร็จ: Vision={len(vision_models)}, Text={len(text_models)}")
            else:
                # ใส่ default model เมื่อ Ollama ไม่พร้อมใช้งาน
                self.vision_model_combo.addItem(self.vision_model)
                self.translation_model_combo.addItem(self.translation_model)
                print("⚠️ Ollama ไม่พร้อมใช้งาน - ใช้ default models")
                
        except Exception as e:
            print(f"❌ Error loading Ollama models: {e}")
            # Fallback ถ้ามีข้อผิดพลาด
            self.vision_model_combo.addItem(self.vision_model)
            self.translation_model_combo.addItem(self.translation_model)
        
        # ตั้งค่า custom prompt
        self.prompt_text.setText(self.custom_prompt)
    
    def on_vision_model_changed(self, model_name):
        """เมื่อเปลี่ยน Vision Model"""
        if model_name and model_name != self.vision_model:
            self.vision_model = model_name
            # อัปเดต OCR ให้ใช้ model ใหม่
            self.ocr.update_vision_model(model_name)
            print(f"🔄 เปลี่ยน Vision Model เป็น: {model_name}")
            
            # อัปเดต config
            OLLAMA_CONFIG['vision_model'] = model_name
    
    def on_translation_model_changed(self, model_name):
        """เมื่อเปลี่ยน Translation Model"""
        if model_name and model_name != self.translation_model:
            self.translation_model = model_name
            # อัปเดต translator ให้ใช้ model ใหม่
            if hasattr(self.translator, 'ollama_translator') and self.translator.ollama_translator:
                self.translator.ollama_translator.update_model(model_name)
            print(f"🔄 เปลี่ยน Translation Model เป็น: {model_name}")
            
            # อัปเดต config
            OLLAMA_CONFIG['translation_model'] = model_name
    
    def on_custom_prompt_changed(self):
        """เมื่อเปลี่ยน Custom Prompt"""
        new_prompt = self.prompt_text.toPlainText().strip()
        if new_prompt != self.custom_prompt:
            self.custom_prompt = new_prompt
            # อัปเดต translator ให้ใช้ prompt ใหม่
            if hasattr(self.translator, 'ollama_translator') and self.translator.ollama_translator:
                self.translator.ollama_translator.update_custom_prompt(new_prompt)
            print(f"🔄 อัปเดต Custom Prompt: {'ใช้' if new_prompt else 'ไม่ใช้ (default)'}")
            
            # อัปเดต config
            OLLAMA_CONFIG['custom_prompt'] = new_prompt
    
    def reset_custom_prompt(self):
        """รีเซ็ต Custom Prompt เป็น default"""
        self.prompt_text.setText("")
        self.custom_prompt = ""
        # อัปเดต translator
        if hasattr(self.translator, 'ollama_translator') and self.translator.ollama_translator:
            self.translator.ollama_translator.update_custom_prompt("")
        print("🔄 รีเซ็ต Custom Prompt เป็น default")
        
        # อัปเดต config
        OLLAMA_CONFIG['custom_prompt'] = ""
        
    def keyPressEvent(self, event):
        """จัดการ keyboard shortcuts"""
        if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            # Ctrl+V สำหรับ toggle visibility
            self.toggle_selection_visibility()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """เมื่อปิดหน้าต่างหลัก"""
        # ยกเลิกและรอ OCR worker
        if self.ocr_worker and self.ocr_worker.isRunning():
            print("🛑 กำลังยกเลิก OCR worker...")
            self.ocr_worker.cancel()
        
        self.selection_widget.close()
        event.accept()


def main():
    """Enhanced main function with Windows-inspired black & white design"""
    app = QApplication(sys.argv)
    
    print("🚀 เริ่มทดสอบ Screen Translator - Windows Theme")
    print("=" * 50)
    print("✨ Design Features:")
    print("   • Translation box at the top")
    print("   • Controls and settings below translation area")
    print("   • Windows-inspired black & white theme")
    print("   • 60% transparent black selection box")
    print("   • Modern Windows UI styling")
    print("")
    print("💡 วิธีการใช้:")
    print("   • เลื่อนเมาส์ไปบนกรอบเพื่อดูการไฮไลท์")
    print("   • คลิกและลากในพื้นที่กรอบเพื่อย้าย")
    print("   • กล่องคำแปลอยู่ด้านบนสุดของหน้าต่าง")
    print("=" * 50)
    
    window = Window()
    window.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
