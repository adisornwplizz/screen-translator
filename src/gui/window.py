import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                            QFrame, QSplitter, QGroupBox, QProgressBar,
                            QCheckBox, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal, QThread, pyqtSlot, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QCursor
import pyautogui
import cv2
import numpy as np
from PIL import Image

# เพิ่ม path สำหรับ import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from translation.ocr import OCR
from translation.translator import Translator
from config import UI_CONFIG


class SelectionWidget(QWidget):
    """Widget สำหรับวาดกรอบเลือกพื้นที่บนหน้าจอ พร้อมความสามารถในการปรับขนาดได้จากทุกทิศทาง"""
    position_changed = pyqtSignal(int, int, int, int)
    
    # กำหนดประเภทการปรับขนาด
    RESIZE_NONE = 0
    RESIZE_TOP = 1
    RESIZE_BOTTOM = 2
    RESIZE_LEFT = 4
    RESIZE_RIGHT = 8
    RESIZE_TOP_LEFT = RESIZE_TOP | RESIZE_LEFT
    RESIZE_TOP_RIGHT = RESIZE_TOP | RESIZE_RIGHT
    RESIZE_BOTTOM_LEFT = RESIZE_BOTTOM | RESIZE_LEFT
    RESIZE_BOTTOM_RIGHT = RESIZE_BOTTOM | RESIZE_RIGHT
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 1);")
        
        # ตำแหน่งและขนาดของกรอบ
        self.selection_rect = QRect(100, 100, 300, 200)
        self.dragging = False
        self.resizing = False
        self.resize_direction = self.RESIZE_NONE
        self.drag_start_pos = None
        self.initial_rect = None
        self.resize_handle_size = 8
        self.resize_border_width = 6
        
        # เปิดใช้งาน mouse tracking เพื่อเปลี่ยน cursor
        self.setMouseTracking(True)
        
        # ตั้งค่าหน้าต่างให้ขยายเต็มหน้าจอ
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # วาดพื้นหลังโปร่งใส
        painter.fillRect(self.rect(), QColor(0, 0, 0, 50))
        
        # วาดพื้นที่ที่เลือก (โปร่งใส)
        painter.fillRect(self.selection_rect, QColor(0, 0, 0, 0))
        
        # วาดเส้นขอบกรอบ
        pen = QPen(QColor(255, 0, 0, 255), 2)
        painter.setPen(pen)
        painter.drawRect(self.selection_rect)
        
        # วาดจุดสำหรับปรับขนาด (handles)
        self.draw_resize_handles(painter)
        
        # วาดข้อมูลขนาด
        self.draw_size_info(painter)
    
    def draw_resize_handles(self, painter):
        """วาดจุดจับสำหรับปรับขนาด"""
        handle_size = self.resize_handle_size
        rect = self.selection_rect
        
        # สีของ handles
        painter.setBrush(QColor(255, 255, 255, 255))
        painter.setPen(QPen(QColor(255, 0, 0, 255), 1))
        
        # มุมทั้ง 4 มุม
        handles = [
            # มุมซ้ายบน
            QRect(rect.left() - handle_size//2, rect.top() - handle_size//2, handle_size, handle_size),
            # มุมขวาบน  
            QRect(rect.right() - handle_size//2, rect.top() - handle_size//2, handle_size, handle_size),
            # มุมซ้ายล่าง
            QRect(rect.left() - handle_size//2, rect.bottom() - handle_size//2, handle_size, handle_size),
            # มุมขวาล่าง
            QRect(rect.right() - handle_size//2, rect.bottom() - handle_size//2, handle_size, handle_size),
            # ตรงกลางด้านบน
            QRect(rect.center().x() - handle_size//2, rect.top() - handle_size//2, handle_size, handle_size),
            # ตรงกลางด้านล่าง
            QRect(rect.center().x() - handle_size//2, rect.bottom() - handle_size//2, handle_size, handle_size),
            # ตรงกลางด้านซ้าย
            QRect(rect.left() - handle_size//2, rect.center().y() - handle_size//2, handle_size, handle_size),
            # ตรงกลางด้านขวา
            QRect(rect.right() - handle_size//2, rect.center().y() - handle_size//2, handle_size, handle_size),
        ]
        
        for handle in handles:
            painter.drawRect(handle)
    
    def draw_size_info(self, painter):
        """วาดข้อมูลขนาดของกรอบ"""
        rect = self.selection_rect
        text = f"{rect.width()} × {rect.height()}"
        
        # กำหนดตำแหน่งข้อความ
        text_pos = QPoint(rect.left(), rect.top() - 10)
        if text_pos.y() < 20:
            text_pos.setY(rect.bottom() + 20)
        
        # วาดพื้นหลังข้อความ
        font = QFont("Arial", 10)
        painter.setFont(font)
        text_rect = painter.fontMetrics().boundingRect(text)
        text_rect.moveTopLeft(text_pos)
        text_rect.adjust(-4, -2, 4, 2)
        
        painter.fillRect(text_rect, QColor(0, 0, 0, 180))
        
        # วาดข้อความ
        painter.setPen(QPen(QColor(255, 255, 255, 255)))
        painter.drawText(text_pos, text)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            
            # ตรวจสอบทิศทางการปรับขนาด
            resize_direction = self.get_resize_direction(pos)
            
            if resize_direction != self.RESIZE_NONE:
                self.resizing = True
                self.resize_direction = resize_direction
                self.drag_start_pos = pos
                self.initial_rect = QRect(self.selection_rect)
            elif self.selection_rect.contains(pos):
                self.dragging = True
                self.drag_start_pos = pos
    
    def mouseMoveEvent(self, event):
        pos = event.pos()
        
        if self.dragging and self.drag_start_pos:
            # ลากกรอบ
            delta = pos - self.drag_start_pos
            new_rect = QRect(self.selection_rect)
            new_rect.translate(delta)
            
            # ตรวจสอบขอบเขตหน้าจอ
            screen_rect = self.rect()
            if (new_rect.left() >= 0 and new_rect.top() >= 0 and 
                new_rect.right() <= screen_rect.width() and 
                new_rect.bottom() <= screen_rect.height()):
                self.selection_rect = new_rect
                self.drag_start_pos = pos
                self.update()
                self.emit_position_changed()
                
        elif self.resizing and self.drag_start_pos and self.initial_rect:
            # ปรับขนาดกรอบ
            self.resize_selection(pos)
            
        else:
            # เปลี่ยน cursor ตามตำแหน่ง
            self.update_cursor(pos)
    
    def resize_selection(self, current_pos):
        """ปรับขนาดกรอบตามทิศทางที่เลือก"""
        delta = current_pos - self.drag_start_pos
        new_rect = QRect(self.initial_rect)
        
        # ปรับขนาดตามทิศทาง
        if self.resize_direction & self.RESIZE_LEFT:
            new_rect.setLeft(new_rect.left() + delta.x())
        if self.resize_direction & self.RESIZE_RIGHT:
            new_rect.setRight(new_rect.right() + delta.x())
        if self.resize_direction & self.RESIZE_TOP:
            new_rect.setTop(new_rect.top() + delta.y())
        if self.resize_direction & self.RESIZE_BOTTOM:
            new_rect.setBottom(new_rect.bottom() + delta.y())
        
        # ตรวจสอบขนาดขั้นต่ำ
        min_size = 50
        if new_rect.width() < min_size:
            if self.resize_direction & self.RESIZE_LEFT:
                new_rect.setLeft(new_rect.right() - min_size)
            else:
                new_rect.setRight(new_rect.left() + min_size)
                
        if new_rect.height() < min_size:
            if self.resize_direction & self.RESIZE_TOP:
                new_rect.setTop(new_rect.bottom() - min_size)
            else:
                new_rect.setBottom(new_rect.top() + min_size)
        
        # ตรวจสอบขอบเขตหน้าจอ
        screen_rect = self.rect()
        new_rect = new_rect.intersected(screen_rect)
        
        # อัปเดตกรอบ
        if new_rect.isValid():
            self.selection_rect = new_rect
            self.update()
            self.emit_position_changed()
    
    def get_resize_direction(self, pos):
        """กำหนดทิศทางการปรับขนาดจากตำแหน่งที่คลิก"""
        rect = self.selection_rect
        handle_size = self.resize_handle_size
        border_width = self.resize_border_width
        
        direction = self.RESIZE_NONE
        
        # ตรวจสอบขอบซ้าย-ขวา
        if abs(pos.x() - rect.left()) <= border_width:
            direction |= self.RESIZE_LEFT
        elif abs(pos.x() - rect.right()) <= border_width:
            direction |= self.RESIZE_RIGHT
            
        # ตรวจสอบขอบบน-ล่าง
        if abs(pos.y() - rect.top()) <= border_width:
            direction |= self.RESIZE_TOP
        elif abs(pos.y() - rect.bottom()) <= border_width:
            direction |= self.RESIZE_BOTTOM
            
        # ตรวจสอบ handles ที่มุม
        corner_handles = [
            (rect.topLeft(), self.RESIZE_TOP_LEFT),
            (rect.topRight(), self.RESIZE_TOP_RIGHT),
            (rect.bottomLeft(), self.RESIZE_BOTTOM_LEFT),
            (rect.bottomRight(), self.RESIZE_BOTTOM_RIGHT),
        ]
        
        for corner, corner_direction in corner_handles:
            corner_rect = QRect(corner.x() - handle_size//2, corner.y() - handle_size//2,
                              handle_size, handle_size)
            if corner_rect.contains(pos):
                return corner_direction
                
        # ตรวจสอบ handles ที่ขอบ
        edge_handles = [
            (QPoint(rect.center().x(), rect.top()), self.RESIZE_TOP),
            (QPoint(rect.center().x(), rect.bottom()), self.RESIZE_BOTTOM),
            (QPoint(rect.left(), rect.center().y()), self.RESIZE_LEFT),
            (QPoint(rect.right(), rect.center().y()), self.RESIZE_RIGHT),
        ]
        
        for edge_point, edge_direction in edge_handles:
            edge_rect = QRect(edge_point.x() - handle_size//2, edge_point.y() - handle_size//2,
                            handle_size, handle_size)
            if edge_rect.contains(pos):
                return edge_direction
        
        return direction
    
    def update_cursor(self, pos):
        """อัปเดต cursor ตามตำแหน่งที่เลื่อน"""
        direction = self.get_resize_direction(pos)
        
        if direction == self.RESIZE_TOP or direction == self.RESIZE_BOTTOM:
            self.setCursor(QCursor(Qt.SizeVerCursor))
        elif direction == self.RESIZE_LEFT or direction == self.RESIZE_RIGHT:
            self.setCursor(QCursor(Qt.SizeHorCursor))
        elif direction == self.RESIZE_TOP_LEFT or direction == self.RESIZE_BOTTOM_RIGHT:
            self.setCursor(QCursor(Qt.SizeFDiagCursor))
        elif direction == self.RESIZE_TOP_RIGHT or direction == self.RESIZE_BOTTOM_LEFT:
            self.setCursor(QCursor(Qt.SizeBDiagCursor))
        elif self.selection_rect.contains(pos):
            self.setCursor(QCursor(Qt.SizeAllCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))
    
    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
        self.resize_direction = self.RESIZE_NONE
        self.drag_start_pos = None
        self.initial_rect = None
    
    def emit_position_changed(self):
        """ส่งสัญญาณเมื่อตำแหน่งหรือขนาดเปลี่ยน"""
        self.position_changed.emit(
            self.selection_rect.x(),
            self.selection_rect.y(),
            self.selection_rect.width(),
            self.selection_rect.height()
        )
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()


class Window(QMainWindow):
    def __init__(self, title="Screen Translator"):
        super().__init__()
        self.title = title
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 800, 600)  # ลดขนาดหน้าต่าง
        
        # สร้าง selection widget
        self.selection_widget = SelectionWidget()
        self.selection_widget.position_changed.connect(self.on_selection_changed)
        
        # ตัวแปรสำหรับ OCR
        self.current_selection = QRect(100, 100, 300, 200)
        self.is_capturing = False
        
        # สร้าง OCR instance
        self.ocr = OCR()
        
        # สร้าง Translator instance - ใช้ Ollama เท่านั้น
        self.translator = Translator(service='ollama')
        
        # การตั้งค่าการแปล - แปลอัตโนมัติเสมอ English to Thai เท่านั้น
        self.auto_translate = True  # เปิดแปลอัตโนมัติเสมอ
        self.target_language = 'th'  # ไทยเท่านั้น
        
        # ข้อความล่าสุดที่ตรวจจับได้
        self.last_detected_text = ""
        
        # สร้าง UI
        self.setup_ui()
        
        # ตั้งค่า timer สำหรับ real-time capture
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self.capture_and_process)
        
    def setup_ui(self):
        """ตั้งค่า UI แบบ minimal และ clean"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout หลัก
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ปุ่มควบคุมหลัก
        control_group = QGroupBox("การควบคุม")
        control_layout = QHBoxLayout(control_group)
        
        self.start_button = QPushButton("🎯 เริ่มการแปล")
        self.start_button.clicked.connect(self.start_capture)
        self.start_button.setStyleSheet("""
            QPushButton { 
                background-color: #4CAF50; 
                color: white; 
                padding: 12px 20px; 
                font-size: 14px;
                font-weight: bold; 
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        
        self.stop_button = QPushButton("⏹️ หยุดการแปล")
        self.stop_button.clicked.connect(self.stop_capture)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton { 
                background-color: #f44336; 
                color: white; 
                padding: 12px 20px; 
                font-size: 14px;
                font-weight: bold; 
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #da190b; }
        """)
        
        self.select_area_button = QPushButton("📐 เลือกพื้นที่")
        self.select_area_button.clicked.connect(self.show_selection)
        self.select_area_button.setStyleSheet("""
            QPushButton { 
                background-color: #2196F3; 
                color: white; 
                padding: 12px 20px; 
                font-size: 14px;
                font-weight: bold; 
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.select_area_button)
        control_layout.addStretch()
        
        # การตั้งค่าความถี่
        frequency_layout = QHBoxLayout()
        frequency_layout.addWidget(QLabel("ความถี่การอัปเดต:"))
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 10)
        self.interval_spinbox.setValue(2)
        self.interval_spinbox.setSuffix(" วินาที")
        self.interval_spinbox.valueChanged.connect(self.update_capture_interval)
        frequency_layout.addWidget(self.interval_spinbox)
        frequency_layout.addStretch()
        
        control_layout.addLayout(frequency_layout)
        
        # ข้อมูลสถานะ
        status_group = QGroupBox("สถานะ")
        status_layout = QVBoxLayout(status_group)
        
        self.position_label = QLabel("ตำแหน่ง: X=100, Y=100, กว้าง=300, สูง=200")
        self.position_label.setStyleSheet("QLabel { font-weight: bold; color: #555; }")
        
        self.status_label = QLabel("สถานะ: พร้อมใช้งาน (แปลอัตโนมัติ English → Thai)")
        self.status_label.setStyleSheet("QLabel { color: #2E7D32; font-weight: bold; }")
        
        status_layout.addWidget(self.position_label)
        status_layout.addWidget(self.status_label)
        
        # พื้นที่แสดงข้อความ - แบบ minimal ไม่มี tabs
        text_group = QGroupBox("ข้อความ")
        text_layout = QVBoxLayout(text_group)
        
        # ข้อความต้นฉบับ (ด้านบน)
        original_label = QLabel("📝 ข้อความต้นฉบับ:")
        original_label.setStyleSheet("QLabel { font-weight: bold; color: #424242; margin-bottom: 5px; }")
        text_layout.addWidget(original_label)
        
        self.detected_text = QTextEdit()
        self.detected_text.setFont(QFont("Tahoma", 12))
        self.detected_text.setMaximumHeight(150)  # จำกัดความสูง
        self.detected_text.setPlaceholderText("ข้อความภาษาอังกฤษที่ตรวจพบจะแสดงที่นี่...")
        self.detected_text.setStyleSheet("""
            QTextEdit { 
                border: 2px solid #E0E0E0; 
                border-radius: 8px; 
                padding: 10px; 
                background-color: #FAFAFA;
            }
        """)
        text_layout.addWidget(self.detected_text)
        
        # ข้อความแปล (ด้านล่าง)
        translation_label = QLabel("🌐 คำแปลภาษาไทย:")
        translation_label.setStyleSheet("QLabel { font-weight: bold; color: #424242; margin-top: 10px; margin-bottom: 5px; }")
        text_layout.addWidget(translation_label)
        
        self.translated_text = QTextEdit()
        self.translated_text.setFont(QFont("Tahoma", 12))
        self.translated_text.setPlaceholderText("คำแปลภาษาไทยจะแสดงที่นี่...")
        self.translated_text.setStyleSheet("""
            QTextEdit { 
                border: 2px solid #4CAF50; 
                border-radius: 8px; 
                padding: 10px; 
                background-color: #F1F8E9;
            }
        """)
        text_layout.addWidget(self.translated_text)
        
        # ปุ่มจัดการ
        action_layout = QHBoxLayout()
        
        self.copy_original_button = QPushButton("📋 คัดลอกต้นฉบับ")
        self.copy_original_button.clicked.connect(self.copy_original_text)
        self.copy_original_button.setStyleSheet("""
            QPushButton { 
                background-color: #757575; 
                color: white; 
                padding: 8px 15px; 
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #616161; }
        """)
        
        self.copy_translation_button = QPushButton("📋 คัดลอกคำแปล")
        self.copy_translation_button.clicked.connect(self.copy_translated_text)
        self.copy_translation_button.setStyleSheet("""
            QPushButton { 
                background-color: #4CAF50; 
                color: white; 
                padding: 8px 15px; 
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        
        self.clear_button = QPushButton("🗑️ ล้างข้อความ")
        self.clear_button.clicked.connect(self.clear_all_text)
        self.clear_button.setStyleSheet("""
            QPushButton { 
                background-color: #FF9800; 
                color: white; 
                padding: 8px 15px; 
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #F57C00; }
        """)
        
        action_layout.addWidget(self.copy_original_button)
        action_layout.addWidget(self.copy_translation_button)
        action_layout.addWidget(self.clear_button)
        action_layout.addStretch()
        
        text_layout.addLayout(action_layout)
        
        # เพิ่ม widgets เข้า layout หลัก
        main_layout.addWidget(control_group)
        main_layout.addWidget(status_group)
        main_layout.addWidget(text_group, 1)  # ให้ text area ขยายได้
        
    def show_selection(self):
        """แสดงหน้าต่างเลือกพื้นที่"""
        self.selection_widget.show()
        self.selection_widget.raise_()
        self.selection_widget.activateWindow()
        
    def on_selection_changed(self, x, y, width, height):
        """เมื่อพื้นที่ที่เลือกเปลี่ยน"""
        self.current_selection = QRect(x, y, width, height)
        self.position_label.setText(f"ตำแหน่ง: X={x}, Y={y}, กว้าง={width}, สูง={height}")
        
    def start_capture(self):
        """เริ่มการจับภาพ real-time"""
        self.is_capturing = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # ซ่อน selection widget
        self.selection_widget.hide()
        
        # เริ่ม timer สำหรับจับภาพ
        interval = self.interval_spinbox.value() * 1000  # แปลงเป็น milliseconds
        self.capture_timer.start(interval)
        
        self.detected_text.append("🔄 เริ่มการจับภาพ...\n")
        
    def stop_capture(self):
        """หยุดการจับภาพ"""
        self.is_capturing = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # หยุด timer
        self.capture_timer.stop()
        
        self.detected_text.append("⏹️ หยุดการจับภาพ\n")
        
    def capture_and_process(self):
        """จับภาพหน้าจอและประมวลผล OCR"""
        try:
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
                # สกัดข้อความพร้อมค่าความมั่นใจ
                text, confidence = self.ocr.get_text_with_confidence(screenshot)
                
                # อัปเดตสถานะ
                self.status_label.setText("สถานะ: กำลังประมวลผล...")
                
                # แสดงข้อความ
                if text.strip():
                    # ตรวจสอบว่าเป็นข้อความใหม่หรือไม่
                    if text != self.last_detected_text:
                        import datetime
                        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                        
                        # เพิ่มข้อความลงในพื้นที่แสดงผล
                        self.detected_text.append(f"🕒 {timestamp} (ความมั่นใจ: {confidence:.1f}%)")
                        self.detected_text.append(f"📝 {text}")
                        self.detected_text.append("─" * 50)
                        
                        # เลื่อนไปที่ข้อความล่าสุด
                        self.detected_text.verticalScrollBar().setValue(
                            self.detected_text.verticalScrollBar().maximum()
                        )
                        
                        # แปลอัตโนมัติเสมอ (เปิดใช้งานตลอด)
                        if self.auto_translate:
                            self.translate_text(text)
                        
                        self.last_detected_text = text
                
                self.status_label.setText("สถานะ: พร้อมใช้งาน (แปลอัตโนมัติ English → Thai)")
            else:
                self.status_label.setText("สถานะ: ไม่สามารถจับภาพได้")
                
        except Exception as e:
            self.detected_text.append(f"❌ เกิดข้อผิดพลาด: {str(e)}")
            self.status_label.setText("สถานะ: เกิดข้อผิดพลาด")
            
    def update_capture_interval(self, value):
        """อัปเดตความถี่ในการจับภาพ"""
        if self.is_capturing:
            self.capture_timer.setInterval(value * 1000)
    
    def clear_all_text(self):
        """ล้างข้อความทั้งหมด"""
        self.detected_text.clear()
        self.translated_text.clear()
        self.last_detected_text = ""
        self.status_label.setText("สถานะ: ล้างข้อความแล้ว")
    
    def closeEvent(self, event):
        """เมื่อปิดหน้าต่างหลัก"""
        self.selection_widget.close()
        event.accept()
    
    def update_target_language(self, language_text):
        """อัปเดตภาษาเป้าหมาย"""
        # แยกรหัสภาษาจากข้อความ (เช่น "ไทย (th)" -> "th")
        self.target_language = language_text.split('(')[-1].replace(')', '')
        
    def translate_current_text(self):
        """แปลข้อความปัจจุบัน"""
        text = self.last_detected_text.strip()
        if not text:
            self.translated_text.append("❌ ไม่มีข้อความให้แปล")
            return
            
        self.translate_text(text)
    
    def translate_text(self, text):
        """แปลข้อความ"""
        try:
            self.status_label.setText("สถานะ: กำลังแปล...")
            
            # ตรวจสอบว่า translator พร้อมใช้งานหรือไม่
            if not self.translator.is_available():
                self.translated_text.append("❌ ระบบแปลภาษาไม่พร้อมใช้งาน")
                self.status_label.setText("สถานะ: ระบบแปลไม่พร้อมใช้งาน")
                return
            
            # แปลข้อความ
            result = self.translator.translate(text, self.target_language)
            
            if result['translated_text']:
                import datetime
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                
                # แสดงผลการแปล
                self.translated_text.append(f"🕒 {timestamp}")
                self.translated_text.append(f"🔍 ภาษาต้นฉบับ: {result['detected_language']}")
                self.translated_text.append(f"📝 ข้อความต้นฉบับ: {text}")
                self.translated_text.append(f"🌐 คำแปล: {result['translated_text']}")
                
                # แสดงข้อมูล service ที่ใช้
                if 'service' in result:
                    service_name = result['service'].title()
                    if 'model' in result:
                        self.translated_text.append(f"⚡ แปลโดย: {service_name} ({result['model']})")
                    else:
                        self.translated_text.append(f"⚡ แปลโดย: {service_name}")
                
                # แสดง error หากมี
                if 'error' in result:
                    self.translated_text.append(f"⚠️ หมายเหตุ: {result['error']}")
                
                self.translated_text.append("─" * 50)
                
                # เลื่อนไปที่ข้อความล่าสุด
                self.translated_text.verticalScrollBar().setValue(
                    self.translated_text.verticalScrollBar().maximum()
                )
                
                self.status_label.setText("สถานะ: แปลสำเร็จ")
            else:
                self.translated_text.append("❌ ไม่สามารถแปลข้อความได้")
                self.status_label.setText("สถานะ: แปลไม่สำเร็จ")
                
        except Exception as e:
            self.translated_text.append(f"❌ เกิดข้อผิดพลาดในการแปล: {str(e)}")
            self.status_label.setText("สถานะ: เกิดข้อผิดพลาดในการแปล")
    
    def copy_original_text(self):
        """คัดลอกข้อความต้นฉบับ"""
        try:
            import pyperclip
            text = self.detected_text.toPlainText()
            pyperclip.copy(text)
            self.status_label.setText("สถานะ: คัดลอกข้อความต้นฉบับแล้ว")
        except:
            # Fallback หาก pyperclip ไม่พร้อมใช้งาน
            clipboard = QApplication.clipboard()
            clipboard.setText(self.detected_text.toPlainText())
            self.status_label.setText("สถานะ: คัดลอกข้อความต้นฉบับแล้ว")
    
    def copy_translated_text(self):
        """คัดลอกข้อความที่แปลแล้ว"""
        try:
            import pyperclip
            text = self.translated_text.toPlainText()
            pyperclip.copy(text)
            self.status_label.setText("สถานะ: คัดลอกคำแปลแล้ว")
        except:
            # Fallback หาก pyperclip ไม่พร้อมใช้งาน
            clipboard = QApplication.clipboard()
            clipboard.setText(self.translated_text.toPlainText())
            self.status_label.setText("สถานะ: คัดลอกคำแปลแล้ว")
    
    def clear_translation(self):
        """ล้างคำแปล"""
        self.translated_text.clear()
    
    def update_translation_service(self, service_text):
        """เปลี่ยน translation service (ปิดใช้งาน - ใช้ Ollama เท่านั้น)"""
        # ปิดใช้งานการเปลี่ยน service - ใช้ Ollama เท่านั้น
        pass
    
    def translate_current_text(self):
        """แปลข้อความปัจจุบัน"""
        text = self.last_detected_text.strip()
        if not text:
            self.translated_text.append("❌ ไม่มีข้อความให้แปล")
            return
            
        self.translate_text(text)
    
    def update_target_language(self, language_text):
        """อัปเดตภาษาเป้าหมาย (ปิดใช้งาน - ใช้ไทยเท่านั้น)"""
        # ปิดใช้งานการเปลี่ยนภาษา - ใช้ไทยเท่านั้น  
        self.target_language = 'th'