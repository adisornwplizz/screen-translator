# 📋 คู่มือการติดตั้ง Screen Translator

## ขั้นตอนการติดตั้งแบบละเอียด

### 1. ติดตั้ง Python 🐍

#### ดาวน์โหลด Python
1. ไปที่ [python.org](https://www.python.org/downloads/)
2. กดปุ่ม **"Download Python 3.11.x"** (เวอร์ชันล่าสุด)
3. รันไฟล์ installer ที่ดาวน์โหลดมา

#### การติดตั้ง Python
1. ✅ **สำคัญ!** ติ๊กเลือก **"Add Python to PATH"** ก่อนกด Install
2. เลือก **"Install Now"**
3. รอให้การติดตั้งเสร็จสิ้น
4. กด **"Close"**

#### ตรวจสอบการติดตั้ง
1. เปิด Command Prompt (Win + R → cmd → Enter)
2. พิมพ์: `python3 --version`
3. ควรเห็น: `Python 3.11.x`

### 2. ติดตั้ง Tesseract OCR 👁️

#### ดาวน์โหลด Tesseract
1. ไปที่ [Tesseract for Windows](https://github.com/UB-Mannheim/tesseract/wiki)
2. กดลิงก์ **"tesseract-ocr-w64-setup-v5.3.0.20221214.exe"** (หรือเวอร์ชันล่าสุด)

#### การติดตั้ง Tesseract
1. รันไฟล์ installer
2. เลือกภาษาที่ต้องการ (ภาษาไทยและอังกฤษ)
3. ติดตั้งที่ตำแหน่งเริ่มต้น: `C:\Program Files\Tesseract-OCR\`
4. กด **"Install"**

#### ตั้งค่า PATH (ถ้าจำเป็น)
1. เปิด **System Properties** (Win + Pause)
2. กด **"Advanced system settings"**
3. กด **"Environment Variables"**
4. ใน **System variables** หา **"Path"** และกด **"Edit"**
5. กด **"New"** และเพิ่ม: `C:\Program Files\Tesseract-OCR`
6. กด **"OK"** ทุกหน้าต่าง

### 3. ติดตั้ง Screen Translator 🎯

#### ดาวน์โหลดโปรเจกต์
```bash
# วิธีที่ 1: ดาวน์โหลด ZIP จาก GitHub
# ไปที่ https://github.com/yourusername/screen-translator
# กด "Code" → "Download ZIP"
# แตกไฟล์ที่ Desktop

# วิธีที่ 2: ใช้ git (ถ้ามี)
git clone https://github.com/yourusername/screen-translator.git
cd screen-translator
```

#### ติดตั้ง Dependencies
1. เปิด Command Prompt หรือ PowerShell
2. ไปที่โฟลเดอร์โปรเจกต์:
   ```bash
   cd Desktop\screen-translator
   ```
3. ติดตั้ง packages:
   ```bash
   pip install -r requirements.txt
   ```

### 4. รันแอปพลิเคชัน 🚀

#### วิธีที่ 1: ใช้ Batch File (แนะนำ)
1. ดับเบิลคลิกไฟล์ `run.bat`
2. รอให้ตรวจสอบและติดตั้ง dependencies
3. แอปพลิเคชันจะเปิดขึ้นมาอัตโนมัติ

#### วิธีที่ 2: รันด้วย Command Line
```bash
cd src
python3 main.py
```

## 🔧 การแก้ปัญหาการติดตั้ง

### ปัญหา: Python ไม่พบ
```
'python' is not recognized as an internal or external command
```
**วิธีแก้**: 
- ติดตั้ง Python ใหม่และติ๊ก "Add Python to PATH"
- หรือเพิ่ม Python ใน PATH manually

### ปัญหา: pip ไม่ทำงาน
```
'pip' is not recognized as an internal or external command
```
**วิธีแก้**:
```bash
python -m pip install -r requirements.txt
```

### ปัญหา: Tesseract ไม่พบ
```
❌ Tesseract ไม่พบในตำแหน่งที่กำหนด
```
**วิธีแก้**:
1. ตรวจสอบว่าติดตั้งที่ `C:\Program Files\Tesseract-OCR\`
2. แก้ไขไฟล์ `src\config.py`:
   ```python
   OCR_CONFIG = {
       'tesseract_cmd': r'C:\Users\YOUR_USERNAME\AppData\Local\Tesseract-OCR\tesseract.exe',  # ปรับ path
       # ...
   }
   ```

### ปัญหา: ModuleNotFoundError
```
ModuleNotFoundError: No module named 'PyQt5'
```
**วิธีแก้**:
```bash
pip install PyQt5
# หรือ
pip install -r requirements.txt
```

### ปัญหา: Google Translate ไม่ทำงาน
```
❌ ระบบแปลภาษาไม่พร้อมใช้งาน
```
**วิธีแก้**:
1. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
2. ติดตั้ง googletrans ใหม่:
   ```bash
   pip uninstall googletrans
   pip install googletrans==4.0.0-rc1
   ```

## 📋 Checklist การติดตั้ง

- [ ] ติดตั้ง Python 3.7+ แล้ว
- [ ] ติ๊ก "Add Python to PATH" ตอนติดตั้ง
- [ ] ติดตั้ง Tesseract OCR แล้ว
- [ ] ติดตั้ง dependencies ด้วย pip แล้ว
- [ ] ทดสอบรันแอปพลิเคชันแล้ว
- [ ] สามารถเลือกพื้นที่และจับภาพได้
- [ ] การแปลภาษาทำงานได้

## 🎯 เริ่มใช้งาน

หลังติดตั้งเสร็จแล้ว:

1. **เลือกพื้นที่**: กดปุ่ม "📐 เลือกพื้นที่" และปรับกรอบแดง
2. **เริ่มจับภาพ**: กดปุ่ม "🎯 เริ่มการจับภาพ"
3. **ตั้งค่าการแปล**: เปิดใช้ "แปลอัตโนมัติ" และเลือกภาษา
4. **ดูผลลัพธ์**: ตรวจสอบข้อความใน tab ต่างๆ

## 💡 เคล็ดลับ

- ใช้กับเกม, เว็บไซต์, หรือแอปต่างประเทศ
- ปรับขนาดพื้นที่ให้เหมาะสมกับข้อความ
- ลองปรับความถี่การจับภาพตามต้องการ
- ใช้คุณสมบัติคัดลอกเพื่อนำข้อความไปใช้ต่อ

---

🆘 **ต้องการความช่วยเหลือ?** สร้าง Issue ใน GitHub หรือติดต่อทีมพัฒนา
