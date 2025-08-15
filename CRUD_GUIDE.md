# Basic CRUD Operations for std01_iot_data Database

This document shows how to perform basic CRUD (Create, Read, Update, Delete) operations on the `std01_iot_data` database.

## Database Structure

The `iot_readings` table has the following structure:
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

## CRUD Operations

### 1. CREATE - Add New Reading

**API Endpoint:** `POST /api/crud/reading`

**Request Body:**
```json
{
    "device_id": "esp32_001",
    "temperature": 23.5,
    "humidity": 65.2,
    "sensor_data": {
        "light": 750,
        "pressure": 1013.25,
        "battery": 85
    }
}
```

**Response:**
```json
{
    "success": true,
    "reading_id": 123,
    "message": "Reading created with ID 123"
}
```

**cURL Example:**
```bash
curl -X POST http://127.0.0.1:5001/api/crud/reading \
  -H "Content-Type: application/json" \
  -d '{"device_id": "esp32_001", "temperature": 23.5, "humidity": 65.2}'
```

### 2. READ - Get Readings

#### Read Specific Reading
**API Endpoint:** `GET /api/crud/reading/{id}`

**Response:**
```json
{
    "success": true,
    "reading": {
        "id": 123,
        "device_id": "esp32_001",
        "temperature": 23.5,
        "humidity": 65.2,
        "sensor_data": {...},
        "timestamp": "2025-08-15 10:30:45",
        "created_at": "2025-08-15 10:30:45"
    }
}
```

#### Read All Readings
**API Endpoint:** `GET /api/crud/readings?limit=100&offset=0`

**Response:**
```json
{
    "success": true,
    "readings": [...],
    "total": 1523,
    "limit": 100,
    "offset": 0
}
```

#### Read Device Readings
**API Endpoint:** `GET /api/crud/device/{device_id}/readings?limit=100&offset=0`

**Response:**
```json
{
    "success": true,
    "device_id": "esp32_001",
    "readings": [...],
    "total": 45,
    "limit": 100,
    "offset": 0
}
```

**cURL Examples:**
```bash
# Get specific reading
curl http://127.0.0.1:5001/api/crud/reading/123

# Get all readings (first 50)
curl "http://127.0.0.1:5001/api/crud/readings?limit=50&offset=0"

# Get device readings
curl http://127.0.0.1:5001/api/crud/device/esp32_001/readings
```

### 3. UPDATE - Modify Reading

**API Endpoint:** `PUT /api/crud/reading/{id}`

**Request Body** (only include fields you want to update):
```json
{
    "temperature": 24.1,
    "humidity": 63.8,
    "sensor_data": {
        "light": 780,
        "pressure": 1012.1,
        "battery": 83,
        "updated": true
    }
}
```

**Response:**
```json
{
    "success": true,
    "message": "Reading 123 updated successfully",
    "rows_affected": 1
}
```

**cURL Example:**
```bash
curl -X PUT http://127.0.0.1:5001/api/crud/reading/123 \
  -H "Content-Type: application/json" \
  -d '{"temperature": 24.1, "humidity": 63.8}'
```

### 4. DELETE - Remove Readings

#### Delete Specific Reading
**API Endpoint:** `DELETE /api/crud/reading/{id}`

**Response:**
```json
{
    "success": true,
    "message": "Reading 123 deleted successfully",
    "rows_affected": 1
}
```

#### Delete All Device Readings
**API Endpoint:** `DELETE /api/crud/device/{device_id}`

**Response:**
```json
{
    "success": true,
    "message": "Deleted 45 readings for device esp32_001",
    "rows_affected": 45
}
```

**cURL Examples:**
```bash
# Delete specific reading
curl -X DELETE http://127.0.0.1:5001/api/crud/reading/123

# Delete all readings for a device
curl -X DELETE http://127.0.0.1:5001/api/crud/device/esp32_001
```

## Python Code Examples

### Using the IoTDataCRUD Class

```python
from app import IoTDataCRUD

# CREATE
result = IoTDataCRUD.create_reading(
    device_id="esp32_001",
    temperature=23.5,
    humidity=65.2,
    sensor_data={"light": 750, "battery": 85}
)
print(result)

# READ
result = IoTDataCRUD.read_reading(123)
print(result['reading'])

# READ ALL
result = IoTDataCRUD.read_all_readings(limit=10, offset=0)
print(f"Total readings: {result['total']}")

# READ DEVICE
result = IoTDataCRUD.read_device_readings("esp32_001", limit=5)
print(f"Device readings: {len(result['readings'])}")

# UPDATE
result = IoTDataCRUD.update_reading(
    reading_id=123,
    temperature=24.1,
    sensor_data={"light": 780, "updated": True}
)
print(result['message'])

# DELETE
result = IoTDataCRUD.delete_reading(123)
print(result['message'])
```

### Using Requests Library

```python
import requests
import json

base_url = "http://127.0.0.1:5001/api/crud"

# CREATE
data = {
    "device_id": "esp32_001",
    "temperature": 23.5,
    "humidity": 65.2
}
response = requests.post(f"{base_url}/reading", json=data)
result = response.json()
reading_id = result['reading_id']

# READ
response = requests.get(f"{base_url}/reading/{reading_id}")
reading = response.json()['reading']

# UPDATE
update_data = {"temperature": 24.1}
response = requests.put(f"{base_url}/reading/{reading_id}", json=update_data)

# DELETE
response = requests.delete(f"{base_url}/reading/{reading_id}")
```

## Testing

Run the test script to verify all CRUD operations:

```bash
python test_crud.py
```

This will:
1. Create multiple test readings
2. Read and display them
3. Update a reading
4. Delete readings
5. Clean up test data

## Error Handling

All CRUD operations return a consistent response format:

**Success Response:**
```json
{
    "success": true,
    "message": "Operation completed",
    "data": {...}
}
```

**Error Response:**
```json
{
    "success": false,
    "error": "Error description"
}
```

## Web Interface

You can also perform CRUD operations through the web interface:

- **View:** http://127.0.0.1:5001/devices
- **Create:** http://127.0.0.1:5001/create
- **Edit:** Click edit button on any reading
- **Delete:** Click delete button on any reading

## Database Connection

All operations use the configured MySQL connection:
- **Host:** 61.19.114.86:54000
- **User:** nathee
- **Database:** std01_iot_data

The system automatically handles:
- Database connection management
- Transaction handling
- Error recovery
- JSON serialization/deserialization
