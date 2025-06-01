# 📱 Screen Translator - Real-time OCR & Translation

แอปพลิเคชัน Windows สำหรับแปลข้อความบนหน้าจอแบบ real-time ด้วย OCR และ AI Translation

## ✨ ฟีเจอร์หลัก

- 🎯 **การจับภาพแบบ Real-time**: ตรวจจับข้อความจากหน้าจอได้ทุกวินาที
- 📐 **กรอบปรับขนาดได้**: สามารถลากและปรับขนาดพื้นที่ที่ต้องการตรวจจับ
- 🌐 **แปลภาษาอัตโนมัติ**: รองรับการแปลหลายภาษาด้วย Google Translate
- 📝 **OCR ความแม่นยำสูง**: ใช้ Tesseract OCR สำหรับการอ่านข้อความ
- 📚 **ตารางคำศัพท์**: สกัดและแสดงคำศัพท์พร้อมความหมายเพื่อการเรียนรู้
- 🎨 **UI ที่ใช้งานง่าย**: ออกแบบด้วย PyQt5 ใช้งานง่าย
- 📋 **คัดลอกได้ทันที**: คัดลอกข้อความต้นฉบับและคำแปลได้
- ⚙️ **การตั้งค่าที่ยืดหยุ่น**: ปรับความถี่การจับภาพและภาษาเป้าหมาย

## 🚀 การติดตั้งและใช้งาน

### ความต้องการของระบบ
- Windows 10/11
- Python 3.7 ขึ้นไป
- Tesseract OCR (จะแนะนำการติดตั้งด้านล่าง)

### ขั้นตอนการติดตั้ง

1. **โคลนโปรเจกต์**
   ```bash
   git clone https://github.com/yourusername/screen-translator.git
   cd screen-translator
   ```

2. **ติดตั้ง Tesseract OCR**
   - ดาวน์โหลดจาก: https://github.com/UB-Mannheim/tesseract/wiki
   - ติดตั้งที่ `C:\Program Files\Tesseract-OCR\`
   - เพิ่ม path ใน environment variables

3. **ติดตั้ง Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **รันแอปพลิเคชัน**
   ```bash
   # วิธีที่ 1: ใช้ batch file
   run.bat
   
   # วิธีที่ 2: รันด้วย Python
   cd src
   python3 main.py
   ```

## 🎮 วิธีการใช้งาน

### การตั้งค่าเริ่มต้น
1. เปิดแอปพลิเคชัน
2. กดปุ่ม **"📐 เลือกพื้นที่"** เพื่อกำหนดตำแหน่งที่ต้องการตรวจจับ
3. ลากและปรับขนาดกรอบสีแดงให้ครอบคลุมข้อความที่ต้องการ
4. กด Escape เพื่อปิดหน้าต่างเลือกพื้นที่

### การใช้งาน
1. กดปุ่ม **"🎯 เริ่มการจับภาพ"**
2. ข้อความที่ตรวจจับได้จะแสดงใน tab **"🔄 คำแปล"**
3. คำศัพท์ที่สกัดได้จะแสดงในตาราง tab **"📚 คำศัพท์"**
4. หากเปิดใช้การแปลอัตโนมัติ คำแปลจะแสดงทันที

### การตั้งค่าการแปล
- ✅ เปิดใช้ **"แปลอัตโนมัติ"** เพื่อแปลทันทีที่ตรวจจับข้อความ
- 🌍 เลือกภาษาเป้าหมายจากรายการ dropdown
- ⏱️ ปรับความถี่การจับภาพ (1-10 วินาที)

### การใช้งานตารางคำศัพท์
- 📚 คำศัพท์จะถูกสกัดอัตโนมัติจากข้อความที่ตรวจจับได้
- 🔤 แสดงคำศัพท์ในคอลัมน์ "Vocabulary"
- 🔤 แสดงความหมายในคอลัมน์ "Meaning"
- 🗑️ ใช้ปุ่ม **"🗑️ ล้างคำศัพท์"** เพื่อลบคำศัพท์ทั้งหมด
- 📊 ดูสถิติจำนวนคำและอัตราการแปลที่ด้านล่าง

## 📁 โครงสร้างโปรเจกต์

```
screen-translator/
├── src/
│   ├── main.py              # Entry point
│   ├── config.py            # การตั้งค่าระบบ
│   ├── gui/
│   │   └── window.py        # GUI หลัก
│   ├── translation/
│   │   ├── ocr.py          # OCR engine
│   │   ├── translator.py    # Translation engine
│   │   └── vocabulary.py    # Vocabulary extraction & management
│   └── utils/
│       └── helpers.py       # Helper functions
├── requirements.txt         # Python dependencies
├── run.bat                 # Batch file สำหรับรัน
├── setup.py               # Setup script
└── README.md             # เอกสารนี้
```

## ⚙️ การตั้งค่า

### OCR Settings (config.py)
```python
OCR_CONFIG = {
    'tesseract_cmd': r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    'language': 'tha+eng',  # ภาษาไทย + อังกฤษ
    'config': '--psm 6'
}
```

### Translation Settings
```python
TRANSLATION_CONFIG = {
    'source_language': 'auto',
    'target_language': 'th',
    'service': 'google'
}
```

## 🌍 ภาษาที่รองรับ

- 🇹🇭 ไทย (th)
- 🇺🇸 อังกฤษ (en)  
- 🇯🇵 ญี่ปุ่น (ja)
- 🇰🇷 เกาหลี (ko)
- 🇨🇳 จีน (zh)
- 🇫🇷 ฝรั่งเศส (fr)
- 🇩🇪 เยอรมัน (de)
- 🇪🇸 สเปน (es)
- และอีกมากมาย...

## 🔧 การแก้ปัญหา

### Tesseract ไม่พบ
```
❌ Tesseract ไม่พบในตำแหน่งที่กำหนด
```
**วิธีแก้**: 
1. ตรวจสอบว่าติดตั้ง Tesseract แล้ว
2. อัปเดต path ในไฟล์ `config.py`
3. เพิ่ม Tesseract ใน PATH environment variable

### ปัญหาการแปล
```
❌ ระบบแปลภาษาไม่พร้อมใช้งาน
```
**วิธีแก้**:
1. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
2. ตรวจสอบว่าติดตั้ง googletrans แล้ว
3. ลองรีสตาร์ทแอปพลิเคชัน

### ประสิทธิภาพช้า
- ลดความถี่การจับภาพ
- ลดขนาดพื้นที่ที่ตรวจจับ
- ปิดการแปลอัตโนมัติ

## 🤝 การพัฒนาต่อ

### TODO List
- [ ] รองรับการบันทึกภาพ
- [ ] เพิ่มการตั้งค่า OCR ขั้นสูง
- [ ] รองรับ API แปลภาษาอื่นๆ
- [ ] เพิ่มฟีเจอร์ hotkey
- [ ] ประวัติการแปล
- [ ] Export ผลลัพธ์เป็นไฟล์

### การมีส่วนร่วม
1. Fork โปรเจกต์
2. สร้าง feature branch
3. Commit การเปลี่ยนแปลง
4. สร้าง Pull Request

## 📄 License

MIT License - ดูรายละเอียดในไฟล์ LICENSE

## 📞 ติดต่อ

- GitHub Issues: สำหรับรายงานข้อผิดพลาด
- Email: your.email@example.com

---

💡 **เคล็ดลับ**: ใช้งานร่วมกับเกมหรือแอปต่างประเทศเพื่อแปลข้อความแบบ real-time!
│   │   ├── translator.py # Handles text translation
│   │   └── ocr.py       # Captures and recognizes text from the screen
│   ├── utils
│   │   └── helpers.py    # Utility functions for various tasks
│   └── config.py        # Configuration settings for the application
├── requirements.txt      # Lists project dependencies
├── setup.py              # Packaging information
└── README.md             # Documentation for the project
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd screen-translator
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the application settings in `src/config.py` as needed.

## Usage

To run the application, execute the following command:
```
python3 src/main.py
```

Follow the on-screen instructions to select the area of the screen you want to capture and translate.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.