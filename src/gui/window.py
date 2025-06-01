import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                            QFrame, QSplitter, QGroupBox, QProgressBar,
                            QCheckBox, QSpinBox, QSlider, QTableWidget, 
                            QTableWidgetItem, QHeaderView)
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
from utils.vocabulary import extract_vocabulary_from_text


class SelectionWidget(QWidget):
    """Enhanced Widget สำหรับวาดกรอบเลือกพื้นที่บนหน้าจอ พร้อมการปรับปรุงการเคลื่อนไหว"""
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
        
        # กำหนดเป็น fullscreen window แบบ tool
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # กำหนดขนาดเต็มหน้าจอ
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(screen)
        
        # ตัวแปรสำหรับการลากและปรับขนาด
        self.selection_rect = QRect(400, 300, 200, 100)
        self.dragging = False
        self.resizing = False
        self.resize_direction = self.RESIZE_NONE
        self.drag_start_pos = None
        self.initial_rect = None
        self.resize_handle_size = 8
        self.resize_border_width = 6
        
        # การจัดการการมองเห็น
        self.visible_mode = True  # สถานะการแสดงผล
        
        # เปิดใช้งาน mouse tracking เพื่อเปลี่ยน cursor
        self.setMouseTracking(True)
        
        # ✨ Enhanced movement feedback - NEW FEATURES
        self.is_hovering_move_area = False
        self.movement_highlight_alpha = 30
        self.smooth_movement = True
        
        # แสดงตลอดเวลา
        self.show()
        
    def get_interactive_region(self):
        """ได้พื้นที่ที่สามารถโต้ตอบได้ (selection rect + resize handles)"""
        if not self.visible_mode:
            return QRect()  # ไม่มีพื้นที่โต้ตอบเมื่อซ่อน
            
        # ขยายกรอบออกไปเพื่อรวม resize handles
        expanded_rect = QRect(self.selection_rect)
        border = self.resize_border_width + self.resize_handle_size
        expanded_rect.adjust(-border, -border, border, border)
        return expanded_rect
        
    def should_handle_mouse_event(self, pos):
        """ตรวจสอบว่าควรจัดการ mouse event หรือไม่"""
        if not self.visible_mode:
            return False
        interactive_region = self.get_interactive_region()
        return interactive_region.contains(pos)
        
    def paintEvent(self, event):
        """✨ Enhanced paint event with improved visual feedback"""
        # ถ้าไม่ต้องการแสดงผล ให้ข้าม
        if not self.visible_mode:
            return
            
        painter = QPainter(self)
        
        # วาดพื้นที่ที่เลือก (โปร่งใส)
        painter.fillRect(self.selection_rect, QColor(0, 0, 0, 0))
        
        # ✨ Highlight moveable area when hovering (NEW FEATURE)
        if self.is_hovering_move_area and not self.resizing:
            highlight_rect = QRect(self.selection_rect)
            highlight_rect.adjust(-2, -2, 2, 2)
            painter.fillRect(highlight_rect, QColor(0, 120, 255, self.movement_highlight_alpha))
        
        # ✨ Dynamic border color based on state (ENHANCED)
        if self.dragging:
            pen_color = QColor(0, 255, 0, 220)  # Green when dragging
            pen_width = 3
        elif self.is_hovering_move_area:
            pen_color = QColor(0, 120, 255, 200)  # Blue when hovering
            pen_width = 2
        else:
            pen_color = QColor(255, 0, 0, 180)  # Red default
            pen_width = 2
            
        pen = QPen(pen_color, pen_width)
        painter.setPen(pen)
        painter.drawRect(self.selection_rect)

        # ✨ Draw move icon (NEW)
        self.draw_move_icon(painter)
        
        # วาดจุดสำหรับปรับขนาด (handles)
        self.draw_resize_handles(painter)
        
        # ✨ Enhanced size info with movement status (IMPROVED)
        self.draw_enhanced_size_info(painter)
    
    def draw_move_icon(self, painter):
        """Draws a small cross icon at the top-left of the selection box."""
        rect = self.selection_rect
        icon_size = 10  # Size of the icon lines
        margin = 8      # Margin from the corner, making it slightly more inset

        # Calculate center of the icon
        icon_center_x = rect.left() + margin + icon_size // 2
        icon_center_y = rect.top() + margin + icon_size // 2

        # Icon pen
        icon_pen = QPen(QColor(80, 80, 80, 180), 2) # Dark grey, semi-transparent
        painter.setPen(icon_pen)

        # Draw horizontal line of the cross
        painter.drawLine(icon_center_x - icon_size // 2, icon_center_y,
                         icon_center_x + icon_size // 2, icon_center_y)
        # Draw vertical line of the cross
        painter.drawLine(icon_center_x, icon_center_y - icon_size // 2,
                         icon_center_x, icon_center_y + icon_size // 2)

    def draw_resize_handles(self, painter):
        """วาดจุดจับสำหรับปรับขนาด"""
        handle_size = self.resize_handle_size
        rect = self.selection_rect
        
        # สีของ handles
        painter.setBrush(QColor(255, 255, 255, 255))
        painter.setPen(QPen(QColor(255, 0, 0, 255), 1))
        
        # มุมทั้ง 4 มุม
        handles = [
            # Corner handles
            QRect(rect.left() - handle_size//2, rect.top() - handle_size//2, handle_size, handle_size),
            QRect(rect.right() - handle_size//2, rect.top() - handle_size//2, handle_size, handle_size),
            QRect(rect.left() - handle_size//2, rect.bottom() - handle_size//2, handle_size, handle_size),
            QRect(rect.right() - handle_size//2, rect.bottom() - handle_size//2, handle_size, handle_size),
            # Edge handles
            QRect(rect.center().x() - handle_size//2, rect.top() - handle_size//2, handle_size, handle_size),
            QRect(rect.center().x() - handle_size//2, rect.bottom() - handle_size//2, handle_size, handle_size),
            QRect(rect.left() - handle_size//2, rect.center().y() - handle_size//2, handle_size, handle_size),
            QRect(rect.right() - handle_size//2, rect.center().y() - handle_size//2, handle_size, handle_size),
        ]
        
        for handle in handles:
            painter.drawRect(handle)
    
    def draw_enhanced_size_info(self, painter):
        """✨ Enhanced size info with movement status (NEW FEATURE)"""
        rect = self.selection_rect
        
        # Main size text
        size_text = f"{rect.width()} × {rect.height()}"
        
        # ✨ Add movement status indicator
        if self.dragging:
            status_text = "🔄 Moving..."
            status_color = QColor(0, 255, 0, 255)
        elif self.is_hovering_move_area:
            status_text = "👆 Click & Drag to Move"
            status_color = QColor(0, 120, 255, 255)
        else:
            status_text = ""
            status_color = QColor(255, 255, 255, 255)
        
        # กำหนดตำแหน่งข้อความ
        text_pos = QPoint(rect.left(), rect.top() - 30)
        if text_pos.y() < 40:
            text_pos.setY(rect.bottom() + 40)
        
        # วาดพื้นหลังข้อความ
        font = QFont("Arial", 10)
        painter.setFont(font)
        
        # Size info
        size_rect = painter.fontMetrics().boundingRect(size_text)
        size_rect.moveTopLeft(text_pos)
        size_rect.adjust(-4, -2, 4, 2)
        
        painter.fillRect(size_rect, QColor(0, 0, 0, 180))
        painter.setPen(QPen(QColor(255, 255, 255, 255)))
        painter.drawText(text_pos, size_text)
        
        # ✨ Status info (NEW)
        if status_text:
            status_pos = QPoint(text_pos.x(), text_pos.y() + 20)
            status_rect = painter.fontMetrics().boundingRect(status_text)
            status_rect.moveTopLeft(status_pos)
            status_rect.adjust(-4, -2, 4, 2)
            
            painter.fillRect(status_rect, QColor(0, 0, 0, 160))
            painter.setPen(QPen(status_color))
            painter.drawText(status_pos, status_text)
    
    def mousePressEvent(self, event):
        """✨ Enhanced mouse press with better feedback (IMPROVED)"""
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            
            # ตรวจสอบว่าควรจัดการ event หรือไม่
            if not self.should_handle_mouse_event(pos):
                event.ignore()
                return
            
            # ตรวจสอบว่าเป็นการปรับขนาดหรือไม่
            resize_direction = self.get_resize_direction(pos)
            
            if resize_direction != self.RESIZE_NONE:
                # เริ่มการปรับขนาด
                self.resizing = True
                self.resize_direction = resize_direction
                self.drag_start_pos = pos
                self.initial_rect = QRect(self.selection_rect)
                event.accept()
            else:
                # ✨ Enhanced dragging - allow from anywhere in interactive region
                self.dragging = True
                self.drag_start_pos = pos
                self.update()  # Trigger immediate visual feedback
                event.accept()
    
    def mouseMoveEvent(self, event):
        """✨ Enhanced mouse move with smooth feedback (IMPROVED)"""
        pos = event.pos()
        
        # ตรวจสอบว่าควรจัดการ event หรือไม่
        if not self.should_handle_mouse_event(pos) and not (self.dragging or self.resizing):
            event.ignore()
            return
        
        if self.dragging and self.drag_start_pos:
            # ✨ Enhanced dragging with smooth movement
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
            # ✨ Enhanced cursor and hover feedback
            self.update_enhanced_cursor(pos)
    
    def update_enhanced_cursor(self, pos):
        """✨ Enhanced cursor with hover feedback (NEW FEATURE)"""
        # ถ้าไม่อยู่ในโหมดแสดงผล ไม่ต้องเปลี่ยน cursor
        if not self.visible_mode:
            self.setCursor(QCursor(Qt.ArrowCursor))
            self.is_hovering_move_area = False
            return
            
        direction = self.get_resize_direction(pos)
        
        # Track hover state changes for visual feedback
        prev_hovering = self.is_hovering_move_area
        self.is_hovering_move_area = False
        
        if direction == self.RESIZE_TOP or direction == self.RESIZE_BOTTOM:
            self.setCursor(QCursor(Qt.SizeVerCursor))
        elif direction == self.RESIZE_LEFT or direction == self.RESIZE_RIGHT:
            self.setCursor(QCursor(Qt.SizeHorCursor))
        elif direction == self.RESIZE_TOP_LEFT or direction == self.RESIZE_BOTTOM_RIGHT:
            self.setCursor(QCursor(Qt.SizeFDiagCursor))
        elif direction == self.RESIZE_TOP_RIGHT or direction == self.RESIZE_BOTTOM_LEFT:
            self.setCursor(QCursor(Qt.SizeBDiagCursor))
        elif self.selection_rect.contains(pos):
            # ✨ Enhanced move cursor with hover state
            self.setCursor(QCursor(Qt.SizeAllCursor))
            self.is_hovering_move_area = True
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))
            
        # ✨ Update visual feedback if hover state changed
        if prev_hovering != self.is_hovering_move_area:
            self.update()  # Trigger repaint for highlight effect
    
    def mouseReleaseEvent(self, event):
        """✨ Enhanced mouse release with cleanup (IMPROVED)"""
        was_dragging = self.dragging
        
        self.dragging = False
        self.resizing = False
        self.resize_direction = self.RESIZE_NONE
        self.drag_start_pos = None
        self.initial_rect = None
        
        # ✨ Update visual feedback when dragging ends
        if was_dragging:
            self.update()
    
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
        elif event.key() == Qt.Key_V:  # V key สำหรับ toggle visibility
            self.toggle_visibility()
    
    def toggle_visibility(self):
        """สลับการแสดงผล โดยที่ยังคงทำงานอยู่"""
        self.visible_mode = not self.visible_mode
        self.update()  # repaint เพื่อแสดง/ซ่อน
        
    def set_visible_mode(self, visible):
        """ตั้งค่าการแสดงผล"""
        self.visible_mode = visible
        self.update()
        
    def is_visible_mode(self):
        """ตรวจสอบสถานะการแสดงผล"""
        return self.visible_mode


# Use the enhanced SelectionWidget in the main Window class
# (The rest of the Window class remains the same as in the original file)
class Window(QMainWindow):
    def __init__(self, title="Screen Translator - Enhanced Movement"):
        super().__init__()
        self.title = title
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 500, 400)
        
        # ✨ Use the enhanced SelectionWidget
        self.selection_widget = SelectionWidget()
        self.selection_widget.position_changed.connect(self.on_selection_changed)
        
        # Rest of initialization...
        self.current_selection = QRect(100, 100, 300, 200)
        self.is_capturing = False
        self.ocr = OCR()
        self.translator = Translator(service='ollama')
        self.auto_translate = True
        self.target_language = 'th'
        self.last_detected_text = ""
        
        # การตั้งค่าระยะเวลาการจับภาพ
        self.capture_interval = UI_CONFIG.get('capture_interval', 2000)  # default 2000ms
        
        self.setup_ui()
        
        # Timer setup
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self.capture_and_process)
        
    def setup_ui(self):
        """ตั้งค่า UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout หลัก
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # ปุ่มควบคุมหลัก
        control_group = QGroupBox("การควบคุม - ✨ Enhanced Movement")
        control_layout = QHBoxLayout(control_group)
        
        self.start_button = QPushButton("🎯 เริ่ม")
        self.start_button.clicked.connect(self.start_capture)
        self.start_button.setStyleSheet("""
            QPushButton { 
                background-color: #4CAF50; 
                color: white; 
                padding: 8px 12px; 
                font-size: 12px;
                font-weight: bold; 
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        
        self.stop_button = QPushButton("⏹️ หยุด")
        self.stop_button.clicked.connect(self.stop_capture)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton { 
                background-color: #f44336; 
                color: white; 
                padding: 8px 12px; 
                font-size: 12px;
                font-weight: bold; 
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #da190b; }
        """)
        
        # ปุ่ม toggle visibility
        self.toggle_button = QPushButton("👁️ ซ่อน/แสดง")
        self.toggle_button.clicked.connect(self.toggle_selection_visibility)
        self.toggle_button.setToolTip("ซ่อน/แสดงกรอบเลือกพื้นที่ (Ctrl+V)")
        self.toggle_button.setStyleSheet("""
            QPushButton { 
                background-color: #2196F3; 
                color: white; 
                padding: 8px 12px; 
                font-size: 12px;
                font-weight: bold; 
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.toggle_button)
        control_layout.addStretch()
        
        # Capture interval control
        interval_group = QGroupBox("การตั้งค่าระยะเวลา")
        interval_layout = QHBoxLayout(interval_group)
        
        interval_label = QLabel("ระยะเวลาจับภาพ (วินาที):")
        self.interval_slider = QSlider(Qt.Horizontal)
        self.interval_slider.setMinimum(UI_CONFIG.get('capture_interval_min', 500) // 1000)  # Convert to seconds
        self.interval_slider.setMaximum(UI_CONFIG.get('capture_interval_max', 10000) // 1000)  # Convert to seconds
        self.interval_slider.setValue(self.capture_interval // 1000)  # Convert to seconds
        self.interval_slider.valueChanged.connect(self.on_interval_changed)
        
        self.interval_value_label = QLabel(f"{self.capture_interval // 1000}s")
        self.interval_value_label.setMinimumWidth(40)
        self.interval_value_label.setStyleSheet("QLabel { font-weight: bold; color: #2E7D32; }")
        
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_slider)
        interval_layout.addWidget(self.interval_value_label)
        
        # Status info
        status_group = QGroupBox("สถานะ - ✨ Enhanced Features")
        status_layout = QVBoxLayout(status_group)
        
        self.position_label = QLabel("ตำแหน่ง: X=100, Y=100, กว้าง=300, สูง=200")
        self.position_label.setStyleSheet("QLabel { font-size: 11px; color: #555; }")
        
        self.status_label = QLabel("สถานะ: พร้อมใช้งาน")
        self.status_label.setStyleSheet("QLabel { color: #2E7D32; font-size: 11px; }")
        
        # ✨ Add movement help text
        self.help_label = QLabel("💡 วิธีการใช้: คลิกและลากบริเวณกรอบเพื่อย้าย | เลื่อนเมาส์เพื่อดูไฮไลท์")
        self.help_label.setStyleSheet("QLabel { font-size: 10px; color: #666; font-style: italic; }")
        self.help_label.setWordWrap(True)
        
        status_layout.addWidget(self.position_label)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.help_label)
        
        # Text area
        text_group = QGroupBox("คำแปล")
        text_layout = QVBoxLayout(text_group)
        
        self.translated_text = QTextEdit()
        self.translated_text.setFont(QFont("Tahoma", 12))
        self.translated_text.setPlaceholderText("คำแปลจะแสดงที่นี่...")
        self.translated_text.setStyleSheet("""
            QTextEdit { 
                border: 1px solid #E0E0E0; 
                border-radius: 6px; 
                padding: 8px; 
                background-color: #FAFAFA;
            }
        """)
        text_layout.addWidget(self.translated_text)
        
        # ✨ เพิ่มตารางคำศัพท์ (Vocabulary Table)
        vocab_label = QLabel("📚 ตารางคำศัพท์")
        vocab_label.setStyleSheet("QLabel { font-weight: bold; font-size: 13px; color: #2E7D32; margin-top: 10px; }")
        text_layout.addWidget(vocab_label)
        
        self.vocabulary_table = QTableWidget()
        self.vocabulary_table.setColumnCount(2)
        self.vocabulary_table.setHorizontalHeaderLabels(["Vocabulary", "Meaning"])
        
        # ตั้งค่าขนาดตาราง
        self.vocabulary_table.setMaximumHeight(200)  # จำกัดความสูง
        self.vocabulary_table.setMinimumHeight(120)  # ความสูงขั้นต่ำ
        
        # ตั้งค่าการแสดงผล
        self.vocabulary_table.horizontalHeader().setStretchLastSection(True)
        self.vocabulary_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.vocabulary_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.vocabulary_table.setColumnWidth(0, 150)  # ความกว้างคอลัมน์ Vocabulary
        
        # ตั้งค่าสไตล์ตาราง
        self.vocabulary_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                background-color: #FAFAFA;
                gridline-color: #E8E8E8;
                selection-background-color: #E3F2FD;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #E0E0E0;
                font-weight: bold;
                color: #424242;
            }
        """)
        
        # ตั้งค่าพฤติกรรมตาราง
        self.vocabulary_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.vocabulary_table.setAlternatingRowColors(True)
        self.vocabulary_table.setShowGrid(True)
        
        # เพิ่มข้อความ placeholder เมื่อไม่มีข้อมูล
        self.vocabulary_table.setPlaceholderText("ยังไม่มีคำศัพท์ กรุณาเริ่มการจับภาพ...")
        
        text_layout.addWidget(self.vocabulary_table)
        
        # Add widgets to main layout
        main_layout.addWidget(control_group)
        main_layout.addWidget(interval_group)
        main_layout.addWidget(status_group)
        main_layout.addWidget(text_group, 1)
        
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
                        # แปลอัตโนมัติเสมอ
                        if self.auto_translate:
                            self.translate_text(text)
                        
                        self.last_detected_text = text
                
                self.status_label.setText("สถานะ: พร้อมใช้งาน")
            else:
                self.status_label.setText("สถานะ: ไม่สามารถจับภาพได้")
                
        except Exception as e:
            self.translated_text.clear()
            self.translated_text.append(f"❌ เกิดข้อผิดพลาด: {str(e)}")
            self.status_label.setText("สถานะ: เกิดข้อผิดพลาด")
    
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
                
                # ✨ อัปเดตตารางคำศัพท์
                self.update_vocabulary_table(text, result.get('detected_language', 'auto'))
                
                self.status_label.setText("สถานะ: แปลสำเร็จ")
            else:
                self.translated_text.clear()
                self.translated_text.append("❌ ไม่สามารถแปลข้อความได้")
                self.status_label.setText("สถานะ: แปลไม่สำเร็จ")
                
        except Exception as e:
            self.translated_text.clear()
            self.translated_text.append(f"❌ เกิดข้อผิดพลาดในการแปล: {str(e)}")
            self.status_label.setText("สถานะ: เกิดข้อผิดพลาดในการแปล")
    
    def update_vocabulary_table(self, source_text, detected_language='auto'):
        """✨ อัปเดตตารางคำศัพท์"""
        try:
            # สกัดคำศัพท์จากข้อความต้นฉบับ
            vocabulary_list = extract_vocabulary_from_text(source_text, detected_language, max_count=8)
            
            # ล้างข้อมูลเก่า
            self.vocabulary_table.setRowCount(0)
            
            if not vocabulary_list:
                # ถ้าไม่มีคำศัพท์ ให้แสดงข้อความแจ้ง
                self.vocabulary_table.setRowCount(1)
                no_vocab_item = QTableWidgetItem("ไม่พบคำศัพท์ที่เหมาะสม")
                no_vocab_item.setStyleSheet("color: #999; font-style: italic;")
                empty_meaning = QTableWidgetItem("-")
                empty_meaning.setStyleSheet("color: #999; font-style: italic;")
                self.vocabulary_table.setItem(0, 0, no_vocab_item)
                self.vocabulary_table.setItem(0, 1, empty_meaning)
                return
            
            # เพิ่มแถวตามจำนวนคำศัพท์
            self.vocabulary_table.setRowCount(len(vocabulary_list))
            
            # แปลคำศัพท์แต่ละคำและใส่ในตาราง
            for i, vocab_word in enumerate(vocabulary_list):
                try:
                    # ใส่คำศัพท์ในคอลัมน์แรก
                    vocab_item = QTableWidgetItem(vocab_word)
                    vocab_item.setStyleSheet("font-weight: 500; color: #333;")
                    self.vocabulary_table.setItem(i, 0, vocab_item)
                    
                    # แปลคำศัพท์เดี่ยว
                    if self.translator.is_available():
                        meaning_result = self.translator.translate(vocab_word, self.target_language)
                        meaning = meaning_result.get('translated_text', 'ไม่สามารถแปลได้')
                        
                        # ถ้าคำแปลเหมือนคำต้นฉบับ ให้แสดงว่าไม่จำเป็นต้องแปล
                        if meaning.lower() == vocab_word.lower():
                            meaning = f"({vocab_word})"
                            
                    else:
                        meaning = "ระบบแปลไม่พร้อมใช้งาน"
                    
                    # ใส่ความหมายในคอลัมน์ที่สอง
                    meaning_item = QTableWidgetItem(meaning)
                    meaning_item.setStyleSheet("color: #555;")
                    self.vocabulary_table.setItem(i, 1, meaning_item)
                    
                except Exception as vocab_error:
                    # ถ้าแปลคำใดไม่ได้ ให้ใส่ข้อความแสดงข้อผิดพลาด
                    error_item = QTableWidgetItem("ข้อผิดพลาด")
                    error_item.setStyleSheet("color: #f44336; font-style: italic;")
                    self.vocabulary_table.setItem(i, 1, error_item)
            
            # ปรับขนาดแถวให้เหมาะสม
            self.vocabulary_table.resizeRowsToContents()
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการอัปเดตตารางคำศัพท์: {e}")
            # ใส่ข้อความแสดงข้อผิดพลาดในตาราง
            self.vocabulary_table.setRowCount(1)
            error_item = QTableWidgetItem("เกิดข้อผิดพลาดในการโหลดคำศัพท์")
            error_item.setStyleSheet("color: #f44336; font-style: italic;")
            self.vocabulary_table.setItem(0, 0, error_item)
            empty_meaning = QTableWidgetItem("")
            self.vocabulary_table.setItem(0, 1, empty_meaning)
    
    def toggle_selection_visibility(self):
        """สลับการแสดงผลของ selection widget"""
        self.selection_widget.toggle_visibility()
        
    def set_selection_visible(self, visible):
        """ตั้งค่าการแสดงผลของ selection widget"""
        self.selection_widget.set_visible_mode(visible)
        
    def keyPressEvent(self, event):
        """จัดการ keyboard shortcuts"""
        if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            # Ctrl+V สำหรับ toggle visibility
            self.toggle_selection_visibility()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """เมื่อปิดหน้าต่างหลัก"""
        self.selection_widget.close()
        event.accept()


def main():
    """✨ Enhanced main function with improved box movement"""
    app = QApplication(sys.argv)
    
    print("🚀 เริ่มทดสอบ Enhanced Screen Translator")
    print("=" * 50)
    print("✨ New Features:")
    print("   • Enhanced box movement with hover feedback")
    print("   • Dynamic border colors (red/blue/green)")
    print("   • Visual highlight when hovering over move area")
    print("   • Improved status indicators")
    print("   • Smooth movement feedback")
    print("")
    print("💡 วิธีการใช้:")
    print("   • เลื่อนเมาส์ไปบนกรอบเพื่อดูการไฮไลท์")
    print("   • คลิกและลากในพื้นที่กรอบเพื่อย้าย")
    print("   • สังเกตการเปลี่ยนสีขอบขณะเคลื่อนที่")
    print("=" * 50)
    
    window = Window()
    window.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
