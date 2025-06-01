"""
SelectionWidget module for screen selection functionality
"""

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QCursor


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
        
        # วาดพื้นที่ที่เลือก (สีดำโปร่งใส 60%)
        painter.fillRect(self.selection_rect, QColor(0, 0, 0, 153))  # 60% transparency = 255 * 0.6 = 153
        
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
        """Handle keyboard events"""
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