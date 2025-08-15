# ระบบจัดการข้อมูล IoT ด้วย Flask

แอปพลิเคชัน Flask สำหรับเก็บรวบรวมข้อมูลจากอุปกรณ์ IoT โดยใช้ MicroPython พร้อมการเชื่อมต่อฐานข้อมูล MySQL

## คุณสมบัติ

- REST API สำหรับรับข้อมูลเซนเซอร์ IoT
- การรวมฐานข้อมูล MySQL
- การดึงข้อมูลเฉพาะอุปกรณ์
- จุดตรวจสอบสถานะระบบ
- รองรับรูปแบบข้อมูล JSON
- ส่วนติดต่อผู้ใช้แบบเว็บสำหรับการจัดการข้อมูล CRUD

## การตั้งค่าฐานข้อมูล

แอปพลิเคชันเชื่อมต่อกับฐานข้อมูล MySQL ของคุณด้วยการตั้งค่าดังนี้:
- **โฮสต์**: 61.19.114.86:54000
- **ผู้ใช้**: nathee
- **ฐานข้อมูล**: std01_iot_data

## จุดเชื่อมต่อ API

### 1. หน้าแรก
- **URL**: `/`
- **วิธีการ**: GET
- **คำอธิบาย**: ข้อมูล API พื้นฐาน

### 2. รับข้อมูล IoT
- **URL**: `/api/data`
- **วิธีการ**: POST
- **Content-Type**: application/json
- **ตัวอย่างข้อมูล**:
```json
{
    "device_id": "device_001",
    "temperature": 25.5,
    "humidity": 60.2,
    "sensor_data": {
        "light": 750,
        "pressure": 1013.25
    }
}
```

### 3. ดึงข้อมูลอุปกรณ์
- **URL**: `/api/data/<device_id>`
- **วิธีการ**: GET
- **คำอธิบาย**: ดึงข้อมูลการอ่าน 100 ครั้งล่าสุดสำหรับอุปกรณ์เฉพาะ

### 4. ตรวจสอบสถานะ
- **URL**: `/api/health`
- **วิธีการ**: GET
- **คำอธิบาย**: ตรวจสอบการเชื่อมต่อ API และฐานข้อมูล

## การติดตั้ง

1. ติดตั้ง Python dependencies:
```bash
pip install -r requirements.txt
```

2. รันแอปพลิเคชัน:
```bash
python app.py
```

API จะพร้อมใช้งานที่ `http://localhost:5001`

## ส่วนติดต่อผู้ใช้แบบเว็บ

เข้าถึงส่วนติดต่อผู้ใช้แบบเว็บที่ `http://localhost:5001` สำหรับการจัดการ CRUD:

- **ดูอุปกรณ์**: `/devices` - แสดงอุปกรณ์ IoT ทั้งหมด
- **เพิ่มข้อมูล**: `/create` - เพิ่มการอ่านเซนเซอร์ใหม่
- **แก้ไขข้อมูล**: คลิกปุ่มแก้ไขในการอ่านใดๆ
- **ลบข้อมูล**: คลิกปุ่มลบในการอ่านใดๆ

## การดำเนินการ CRUD

### สร้าง (Create)
```bash
curl -X POST http://127.0.0.1:5001/api/crud/reading \
  -H "Content-Type: application/json" \
  -d '{"device_id":"esp32_001","temperature":23.5,"humidity":65.2}'
```

### อ่าน (Read)
```bash
# ดูข้อมูลการอ่านเฉพาะ
curl http://127.0.0.1:5001/api/crud/reading/123

# ดูข้อมูลทั้งหมด
curl "http://127.0.0.1:5001/api/crud/readings?limit=50&offset=0"

# ดูข้อมูลอุปกรณ์
curl http://127.0.0.1:5001/api/crud/device/esp32_001/readings
```

### อัปเดต (Update)
```bash
curl -X PUT http://127.0.0.1:5001/api/crud/reading/123 \
  -H "Content-Type: application/json" \
  -d '{"temperature":24.1,"humidity":63.8}'
```

### ลบ (Delete)
```bash
# ลบการอ่านเฉพาะ
curl -X DELETE http://127.0.0.1:5001/api/crud/reading/123

# ลบข้อมูลทั้งหมดของอุปกรณ์
curl -X DELETE http://127.0.0.1:5001/api/crud/device/esp32_001
```

## ตัวอย่าง MicroPython Client

นี่คือสคริปต์ MicroPython พื้นฐานสำหรับส่งข้อมูลไปยัง Flask API ของคุณ:

```python
import urequests
import json
import network
import time

# การตั้งค่า WiFi
WIFI_SSID = "ชื่อ_wifi_ของคุณ"
WIFI_PASSWORD = "รหัสผ่าน_wifi_ของคุณ"

# การตั้งค่า API
API_URL = "http://ip_เซิร์ฟเวอร์_ของคุณ:5001/api/data"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    while not wlan.isconnected():
        time.sleep(1)
    
    print("เชื่อมต่อ WiFi สำเร็จ:", wlan.ifconfig())

def send_sensor_data(device_id, temperature, humidity, sensor_data=None):
    data = {
        "device_id": device_id,
        "temperature": temperature,
        "humidity": humidity,
        "sensor_data": sensor_data or {}
    }
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = urequests.post(
            API_URL, 
            data=json.dumps(data), 
            headers=headers
        )
        
        print("การตอบสนอง:", response.status_code, response.text)
        response.close()
        
    except Exception as e:
        print("ข้อผิดพลาดในการส่งข้อมูล:", e)

# การทำงานหลัก
if __name__ == "__main__":
    connect_wifi()
    
    # ส่งข้อมูลตัวอย่าง
    send_sensor_data(
        device_id="esp32_001",
        temperature=26.8,
        humidity=58.3,
        sensor_data={
            "light": 820,
            "pressure": 1012.5
        }
    )
```

## โครงสร้างฐานข้อมูล

แอปพลิเคชันสร้างตารางชื่อ `iot_readings` ที่มีโครงสร้างดังนี้:

```sql
CREATE TABLE iot_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id VARCHAR(100) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    sensor_data JSON,
    temperature FLOAT,
    humidity FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## การทดสอบ

รันสคริปต์ทดสอบเพื่อตรวจสอบการทำงานของ CRUD ทั้งหมด:

```bash
python test_crud.py
```

สคริปต์นี้จะ:
1. สร้างข้อมูลการอ่านทดสอบหลายรายการ
2. อ่านและแสดงข้อมูล
3. อัปเดตข้อมูลการอ่าน
4. ลบข้อมูลการอ่าน
5. ทำความสะอาดข้อมูลทดสอบ

## การพัฒนา

- แอปพลิเคชันทำงานในโหมด debug โดยค่าเริ่มต้น
- ตารางฐานข้อมูลจะถูกสร้างโดยอัตโนมัติเมื่อรันครั้งแรก
- ตรวจสอบ `/api/health` เพื่อยืนยันการเชื่อมต่อฐานข้อมูล

## หมายเหตุด้านความปลอดภัย

- พิจารณาการใช้งานระบบพิสูจน์ตัวตนสำหรับการใช้งานจริง
- ตรวจสอบและกรองข้อมูลที่ป้อนเข้า
- ใช้ตัวแปรสภาพแวดล้อมสำหรับการตั้งค่าที่ละเอียดอ่อน
- ใช้งาน rate limiting สำหรับจุดเชื่อมต่อ API

## การแก้ไขปัญหา

### ไม่สามารถเชื่อมต่อฐานข้อมูลได้
1. ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต
2. ยืนยัน IP และพอร์ตของฐานข้อมูล
3. ตรวจสอบข้อมูลประจำตัวผู้ใช้

### พอร์ต 5000 ถูกใช้งาน
- แอปพลิเคชันใช้พอร์ต 5001 แทน
- หรือเปลี่ยนพอร์ตในไฟล์ `app.py`

### ข้อผิดพลาด JSON
- ตรวจสอบรูปแบบ JSON ในข้อมูล `sensor_data`
- ใช้เครื่องมือตรวจสอบ JSON ออนไลน์

## การสนับสนุน

สำหรับความช่วยเหลือหรือคำถาม:
1. ตรวจสอบไฟล์ `CRUD_GUIDE.md` สำหรับตัวอย่างการใช้งาน API
2. ดูไฟล์ log ของแอปพลิเคชันสำหรับข้อผิดพลาด
3. ทดสอบการเชื่อมต่อฐานข้อมูลด้วย `/api/health`
