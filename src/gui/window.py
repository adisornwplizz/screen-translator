import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                            QFrame, QSplitter, QGroupBox, QProgressBar,
                            QCheckBox, QSpinBox, QSlider, QComboBox)
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
    def __init__(self, title="Screen Translator"):
        super().__init__()
        self.title = title
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 800, 700)  # เพิ่มความกว้างและสูงเพื่อรองรับ 4 columns
        
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
        """ตั้งค่า UI - Windows Black & White Theme"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # ตั้งค่า Windows-inspired styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
                color: #000000;
            }
            QWidget {
                background-color: #ffffff;
                color: #000000;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 11px;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f8f8f8;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: #ffffff;
                color: #000000;
            }
        """)
        
        # Layout หลัก
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 1. กล่องคำแปลอยู่ด้านบนสุด
        text_group = QGroupBox("📄 คำแปล")
        text_layout = QVBoxLayout(text_group)
        
        self.translated_text = QTextEdit()
        self.translated_text.setFont(QFont("Segoe UI", 12))
        self.translated_text.setPlaceholderText("คำแปลจะแสดงที่นี่...")
        self.translated_text.setStyleSheet("""
            QTextEdit { 
                border: 2px solid #cccccc; 
                border-radius: 4px; 
                padding: 8px; 
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
            }
            QTextEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        text_layout.addWidget(self.translated_text)
        main_layout.addWidget(text_group, 1)  # ให้พื้นที่มากที่สุด
        
        # 2. ปุ่มควบคุมและการตั้งค่าอยู่ด้านล่างในรูปแบบ 3 column
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)
        
        # Column 1: การควบคุม
        control_group = QGroupBox("🎮 การควบคุม")
        control_layout = QVBoxLayout(control_group)
        
        self.start_button = QPushButton("▶️ เริ่ม")
        self.start_button.clicked.connect(self.start_capture)
        self.start_button.setStyleSheet("""
            QPushButton { 
                background-color: #0078d4; 
                color: white; 
                padding: 8px 16px; 
                font-size: 11px;
                font-weight: bold; 
                border: 1px solid #005a9e;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover { 
                background-color: #106ebe; 
                border: 1px solid #005a9e;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #f3f2f1;
                color: #a19f9d;
                border: 1px solid #d2d0ce;
            }
        """)
        
        self.stop_button = QPushButton("⏸️ หยุด")
        self.stop_button.clicked.connect(self.stop_capture)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton { 
                background-color: #d83b01; 
                color: white; 
                padding: 8px 16px; 
                font-size: 11px;
                font-weight: bold; 
                border: 1px solid #a4262c;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover { 
                background-color: #f2583e; 
                border: 1px solid #a4262c;
            }
            QPushButton:pressed {
                background-color: #a4262c;
            }
            QPushButton:disabled {
                background-color: #f3f2f1;
                color: #a19f9d;
                border: 1px solid #d2d0ce;
            }
        """)
        
        # ปุ่ม toggle visibility
        self.toggle_button = QPushButton("👁️ ซ่อน/แสดง")
        self.toggle_button.clicked.connect(self.toggle_selection_visibility)
        self.toggle_button.setToolTip("ซ่อน/แสดงกรอบเลือกพื้นที่ (Ctrl+V)")
        self.toggle_button.setStyleSheet("""
            QPushButton { 
                background-color: #ffffff; 
                color: #323130; 
                padding: 8px 16px; 
                font-size: 11px;
                font-weight: normal; 
                border: 1px solid #8a8886;
                border-radius: 3px;
                min-width: 100px;
            }
            QPushButton:hover { 
                background-color: #f3f2f1; 
                border: 1px solid #323130;
            }
            QPushButton:pressed {
                background-color: #edebe9;
            }
        """)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.toggle_button)
        bottom_layout.addWidget(control_group)
        
        # Column 2: การตั้งค่าระยะเวลา
        interval_group = QGroupBox("⏱️ การตั้งค่าระยะเวลา")
        interval_layout = QVBoxLayout(interval_group)
        
        interval_label = QLabel("ระยะเวลาจับภาพ (วินาที):")
        interval_label.setStyleSheet("QLabel { color: #323130; font-size: 11px; }")
        
        self.interval_slider = QSlider(Qt.Horizontal)
        self.interval_slider.setMinimum(UI_CONFIG.get('capture_interval_min', 500) // 1000)  
        self.interval_slider.setMaximum(UI_CONFIG.get('capture_interval_max', 10000) // 1000)  
        self.interval_slider.setValue(self.capture_interval // 1000)  
        self.interval_slider.valueChanged.connect(self.on_interval_changed)
        self.interval_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #d2d0ce;
                height: 6px;
                background: #f3f2f1;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #005a9e;
                width: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #106ebe;
            }
        """)
        
        self.interval_value_label = QLabel(f"{self.capture_interval // 1000}s")
        self.interval_value_label.setMinimumWidth(40)
        self.interval_value_label.setStyleSheet("QLabel { font-weight: bold; color: #0078d4; font-size: 11px; }")
        
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_slider)
        interval_layout.addWidget(self.interval_value_label)
        bottom_layout.addWidget(interval_group)
        
        # Column 3: สถานะ
        status_group = QGroupBox("📊 สถานะ")
        status_layout = QVBoxLayout(status_group)
        
        self.position_label = QLabel("ตำแหน่ง: X=100, Y=100, กว้าง=300, สูง=200")
        self.position_label.setStyleSheet("QLabel { font-size: 10px; color: #605e5c; }")
        
        self.status_label = QLabel("สถานะ: พร้อมใช้งาน")
        self.status_label.setStyleSheet("QLabel { color: #107c10; font-size: 10px; font-weight: bold; }")
        
        # Help text
        self.help_label = QLabel("💡 วิธีการใช้: คลิกและลากบริเวณกรอบเพื่อย้าย | เลื่อนเมาส์เพื่อดูไฮไลท์")
        self.help_label.setStyleSheet("QLabel { font-size: 9px; color: #8a8886; font-style: italic; }")
        self.help_label.setWordWrap(True)
        
        status_layout.addWidget(self.position_label)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.help_label)
        bottom_layout.addWidget(status_group)
        
        # Column 4: การตั้งค่า Ollama Models
        ollama_group = QGroupBox("🤖 การตั้งค่า Ollama")
        ollama_layout = QVBoxLayout(ollama_group)
        
        # Vision Model Selection
        vision_label = QLabel("AI Vision Model:")
        vision_label.setStyleSheet("QLabel { color: #323130; font-size: 11px; }")
        
        self.vision_model_combo = QComboBox()
        self.vision_model_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #8a8886;
                border-radius: 3px;
                padding: 4px;
                background-color: #ffffff;
                color: #323130;
                font-size: 10px;
            }
            QComboBox:drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #8a8886;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #323130;
                width: 6px;
                height: 6px;
                border-top: none;
                border-right: none;
                border-bottom-right-radius: 1px;
            }
        """)
        self.vision_model_combo.currentTextChanged.connect(self.on_vision_model_changed)
        
        # Translation Model Selection
        translation_label = QLabel("Translation Model:")
        translation_label.setStyleSheet("QLabel { color: #323130; font-size: 11px; }")
        
        self.translation_model_combo = QComboBox()
        self.translation_model_combo.setStyleSheet(self.vision_model_combo.styleSheet())
        self.translation_model_combo.currentTextChanged.connect(self.on_translation_model_changed)
        
        # Custom Prompt
        prompt_label = QLabel("Custom Prompt:")
        prompt_label.setStyleSheet("QLabel { color: #323130; font-size: 11px; }")
        
        self.prompt_text = QTextEdit()
        self.prompt_text.setMaximumHeight(80)
        self.prompt_text.setPlaceholderText("ใส่ custom prompt หรือเว้นว่างเพื่อใช้ default...")
        self.prompt_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #8a8886;
                border-radius: 3px;
                padding: 4px;
                background-color: #ffffff;
                color: #323130;
                font-size: 10px;
            }
        """)
        self.prompt_text.textChanged.connect(self.on_custom_prompt_changed)
        
        # Reset Prompt Button
        self.reset_prompt_btn = QPushButton("🔄 รีเซ็ต")
        self.reset_prompt_btn.clicked.connect(self.reset_custom_prompt)
        self.reset_prompt_btn.setStyleSheet("""
            QPushButton {
                background-color: #f3f2f1;
                color: #323130;
                padding: 4px 8px;
                font-size: 10px;
                border: 1px solid #8a8886;
                border-radius: 3px;
                max-width: 60px;
            }
            QPushButton:hover {
                background-color: #e1dfdd;
            }
        """)
        
        ollama_layout.addWidget(vision_label)
        ollama_layout.addWidget(self.vision_model_combo)
        ollama_layout.addWidget(translation_label)
        ollama_layout.addWidget(self.translation_model_combo)
        ollama_layout.addWidget(prompt_label)
        ollama_layout.addWidget(self.prompt_text)
        ollama_layout.addWidget(self.reset_prompt_btn)
        bottom_layout.addWidget(ollama_group)
        
        # เพิ่ม layout 4 column ลงใน main layout
        main_layout.addLayout(bottom_layout)
        
        # โหลด Ollama models เมื่อเริ่มต้น
        self.load_ollama_models()
        
    def on_selection_changed(self, x, y, width, height):
        """เมื่อพื้นที่ที่เลือกเปลี่ยน"""
        self.current_selection = QRect(x, y, width, height)
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
        
        self.status_label.setText(f"สถานะ: เริ่มการจับภาพ (ทุก {self.capture_interval//1000} วินาที)")
        
    def stop_capture(self):
        """หยุดการจับภาพ"""
        self.is_capturing = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # หยุด timer
        self.capture_timer.stop()
        
        self.status_label.setText("สถานะ: หยุดการจับภาพ")
        
    def capture_and_process(self):
        """จับภาพหน้าจอและประมวลผล OCR"""
        try:
            # ตรวจสอบว่า OCR worker ยังทำงานอยู่หรือไม่
            if self.ocr_worker and self.ocr_worker.isRunning():
                print("⚠️ OCR ยังทำงานอยู่ ข้าม capture ครั้งนี้")
                return
                
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
                self.status_label.setText("สถานะ: กำลังอ่านข้อความ...")
                self.ocr_worker.start()
            else:
                self.status_label.setText("สถานะ: ไม่สามารถจับภาพได้")
                
        except Exception as e:
            self.translated_text.clear()
            self.translated_text.append(f"❌ เกิดข้อผิดพลาด: {str(e)}")
            self.status_label.setText("สถานะ: เกิดข้อผิดพลาด")
    
    @pyqtSlot(str, float)
    def on_ocr_finished(self, text, confidence):
        """เมื่อ OCR เสร็จสิ้น"""
        try:
            self.status_label.setText("สถานะ: กำลังประมวลผล...")
            
            # แสดงข้อความ
            if text.strip():
                # ตรวจสอบว่าเป็นข้อความใหม่หรือไม่
                if text != self.last_detected_text:
                    # แปลอัตโนมัติเสมอ
                    if self.auto_translate:
                        self.translate_text(text)
                    
                    self.last_detected_text = text
            
            self.status_label.setText("สถานะ: พร้อมใช้งาน")
            
        except Exception as e:
            self.on_ocr_error(str(e))
    
    @pyqtSlot(str)
    def on_ocr_error(self, error_message):
        """เมื่อ OCR เกิดข้อผิดพลาด"""
        self.translated_text.clear()
        self.translated_text.append(f"❌ เกิดข้อผิดพลาด OCR: {error_message}")
        self.status_label.setText("สถานะ: เกิดข้อผิดพลาด OCR")
    
    def translate_text(self, text):
        """แปลข้อความ"""
        try:
            self.status_label.setText("สถานะ: กำลังแปล...")
            
            # ตรวจสอบว่า translator พร้อมใช้งานหรือไม่
            if not self.translator.is_available():
                self.translated_text.clear()
                self.translated_text.append("❌ ระบบแปลภาษาไม่พร้อมใช้งาน")
                self.status_label.setText("สถานะ: ระบบแปลไม่พร้อมใช้งาน")
                return
            
            # แปลข้อความ
            result = self.translator.translate(text, self.target_language)
            
            if result['translated_text']:
                # Auto clean old content when new text arrives
                self.translated_text.clear()
                
                # แสดงเฉพาะคำแปล
                self.translated_text.append(f"{result['translated_text']}")
                
                # เลื่อนไปที่ข้อความล่าสุด
                self.translated_text.verticalScrollBar().setValue(
                    self.translated_text.verticalScrollBar().maximum()
                )
                
                self.status_label.setText("สถานะ: แปลสำเร็จ")
            else:
                self.translated_text.clear()
                self.translated_text.append("❌ ไม่สามารถแปลข้อความได้")
                self.status_label.setText("สถานะ: แปลไม่สำเร็จ")
                
        except Exception as e:
            self.translated_text.clear()
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
