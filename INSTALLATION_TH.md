# คำแนะนำการติดตั้งและใช้งาน - ระบบจัดการข้อมูล IoT

## ข้อกำหนดระบบ

- Python 3.8 หรือใหม่กว่า
- การเชื่อมต่ออินเทอร์เน็ต
- ฐานข้อมูล MySQL (ถ้าต้องการใช้งานจริง)

## การติดตั้ง

### 1. ดาวน์โหลดโครงการ

```bash
git clone https://github.com/natheelic/crud-flask-iot.git
cd crud-flask-iot
```

### 2. สร้าง Virtual Environment

```bash
python -m venv .venv
```

### 3. เปิดใช้งาน Virtual Environment

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

### 4. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 5. รันแอปพลิเคชัน

```bash
python app.py
```

แอปพลิเคชันจะทำงานที่: `http://127.0.0.1:5001`

## การใช้งาน

### ส่วนติดต่อผู้ใช้แบบเว็บ

1. **หน้าแรก** (`/`) - หน้าหลักของระบบ
2. **ดูอุปกรณ์** (`/devices`) - แสดงรายการอุปกรณ์ IoT ทั้งหมด
3. **เพิ่มข้อมูล** (`/create`) - เพิ่มข้อมูลเซนเซอร์ใหม่
4. **แก้ไขข้อมูล** - คลิกปุ่มแก้ไขในตารางข้อมูล
5. **ลบข้อมูล** - คลิกปุ่มลบในตารางข้อมูล

### API Endpoints

#### สำหรับอุปกรณ์ IoT:
- `POST /api/data` - ส่งข้อมูลเซนเซอร์

#### สำหรับ CRUD Operations:
- `GET /api/crud/readings` - ดึงข้อมูลทั้งหมด
- `POST /api/crud/reading` - เพิ่มข้อมูลใหม่
- `GET /api/crud/reading/{id}` - ดึงข้อมูลเฉพาะ
- `PUT /api/crud/reading/{id}` - อัปเดตข้อมูล
- `DELETE /api/crud/reading/{id}` - ลบข้อมูล

## การตั้งค่าฐานข้อมูล

### ฐานข้อมูลเริ่มต้น

แอปพลิเคชันได้ตั้งค่าเชื่อมต่อกับฐานข้อมูล MySQL แล้ว:
- **โฮสต์:** 61.19.114.86:54000
- **ผู้ใช้:** nathee
- **ฐานข้อมูล:** iot_data

### การเปลี่ยนแปลงการตั้งค่า

หากต้องการใช้ฐานข้อมูลของคุณเอง แก้ไขในไฟล์ `app.py`:

```python
DB_CONFIG = {
    'host': 'your_host',
    'port': 3306,
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database'
}
```

## ตัวอย่างการใช้งานกับ MicroPython

```python
import urequests
import json

# การตั้งค่า
API_URL = "http://your_server_ip:5001/api/data"
DEVICE_ID = "esp32_room_01"

def send_data(temp, humidity):
    data = {
        "device_id": DEVICE_ID,
        "temperature": temp,
        "humidity": humidity,
        "sensor_data": {
            "location": "ห้องนอน",
            "battery": 85.5
        }
    }
    
    try:
        response = urequests.post(
            API_URL,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        print("ส่งข้อมูลสำเร็จ:", response.status_code)
        response.close()
    except Exception as e:
        print("ข้อผิดพลาด:", e)

# ส่งข้อมูล
send_data(28.5, 65.3)
```

## การทดสอบ

### ทดสอบ CRUD Operations

```bash
python test_crud.py
```

### ทดสอบผ่านเว็บเบราว์เซอร์

1. เปิดเว็บเบราว์เซอร์
2. ไปที่ `http://127.0.0.1:5001`
3. ทดสอบการเพิ่ม แก้ไข และลบข้อมูล

## การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

**1. Port 5000 ถูกใช้งาน**
- แอปพลิเคชันใช้ port 5001 แทน
- หรือปิดแอพ AirPlay ใน System Preferences (macOS)

**2. ไม่สามารถเชื่อมต่อฐานข้อมูล**
- ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
- ตรวจสอบข้อมูลการเชื่อมต่อฐานข้อมูล
- ตรวจสอบ firewall settings

**3. ข้อผิดพลาด JSON**
- ตรวจสอบรูปแบบ JSON ในช่อง sensor_data
- ใช้เครื่องมือตรวจสอบ JSON

**4. แบบอักษรไม่แสดงผลถูกต้อง**
- ตรวจสอบว่าเบราว์เซอร์รองรับ Google Fonts
- ตรวจสอบการเชื่อมต่ออินเทอร์เน็ตสำหรับโหลดฟอนต์

## คำสั่งที่มีประโยชน์

```bash
# ตรวจสอบสถานะแอปพลิเคชัน
curl http://127.0.0.1:5001/api/health

# ดึงข้อมูลทั้งหมด
curl http://127.0.0.1:5001/api/crud/readings

# ส่งข้อมูลทดสอบ
curl -X POST http://127.0.0.1:5001/api/data \
  -H "Content-Type: application/json" \
  -d '{"device_id":"test_001","temperature":25.5,"humidity":60.2}'
```

## การพัฒนาต่อ

### เพิ่มฟีเจอร์ใหม่

1. **การพิสูจน์ตัวตน** - เพิ่มระบบ login/logout
2. **Dashboard** - สร้างกราฟแสดงข้อมูล
3. **การแจ้งเตือน** - ส่ง notification เมื่อข้อมูลผิดปกติ
4. **การส่งออกข้อมูล** - export เป็น CSV/Excel

### การปรับแต่ง UI

1. แก้ไขไฟล์ `templates/*.html` สำหรับ HTML
2. แก้ไขไฟล์ `static/css/style.css` สำหรับ CSS  
3. แก้ไขไฟล์ `static/js/app.js` สำหรับ JavaScript

## การสนับสนุน

หากต้องการความช่วยเหลือ:

1. ตรวจสอบไฟล์ `README_TH.md` และ `CRUD_GUIDE.md`
2. ดูข้อความ error ในคอนโซลของเบราว์เซอร์
3. ตรวจสอบ log ของแอปพลิเคชัน
4. ทดสอบการเชื่อมต่อด้วย `/api/health`

---

**หมายเหตุ:** ระบบนี้พัฒนาขึ้นสำหรับการใช้งานทดสอบและเรียนรู้ สำหรับการใช้งานจริงควรเพิ่มระบบความปลอดภัยและการจัดการข้อผิดพลาดที่ครบถ้วนมากขึ้น
