# Flask IoT Data Management System - Endpoints & Pages Documentation

This document provides a detailed description of all pages, endpoints, and their functions in the Flask IoT Data Management System.

## Table of Contents

- [Web Pages (UI)](#web-pages-ui)
- [API Endpoints](#api-endpoints)
- [CRUD API Endpoints](#crud-api-endpoints)
- [Database Operations](#database-operations)
- [Error Handling](#error-handling)

---

## Web Pages (UI)

### 1. Home Page (`/`)
**Route:** `GET /`  
**Function:** `home()`  
**Template:** `templates/index.html`  
**Purpose:** Main dashboard and landing page for the web interface

**Features:**
- Welcome message and system overview
- Navigation cards to main features:
  - View Devices (ดูอุปกรณ์)
  - Add Reading (เพิ่มข้อมูล)
  - API Access (เข้าถึง API)
  - Health Check (ตรวจสอบสถานะ)
- Feature list and API endpoint information
- Getting started instructions

**User Flow:** Entry point → Navigate to specific functionality

---

### 2. Devices List (`/devices`)
**Route:** `GET /devices`  
**Function:** `list_devices()`  
**Template:** `templates/devices.html`  
**Purpose:** Display all IoT devices with summary statistics

**Features:**
- Card-based layout showing each device
- Device statistics:
  - Total readings count
  - Last seen timestamp
  - Average temperature
  - Average humidity
- Quick access to device details
- Add new reading button

**Database Operations:**
```sql
SELECT device_id, MAX(timestamp) as last_seen, COUNT(*) as total_readings,
       AVG(temperature) as avg_temperature, AVG(humidity) as avg_humidity
FROM iot_readings GROUP BY device_id ORDER BY last_seen DESC
```

**User Flow:** Home → View Devices → Individual Device Details

---

### 3. Device Details (`/device/<device_id>`)
**Route:** `GET /device/<device_id>`  
**Function:** `view_device(device_id)`  
**Template:** `templates/device_detail.html`  
**Purpose:** Detailed view of all readings for a specific device

**Features:**
- Paginated table of all device readings (20 per page)
- Reading details: ID, timestamp, temperature, humidity, sensor data
- Expandable sensor data JSON viewer
- Edit and delete actions for each reading
- Pagination controls
- Device-specific statistics

**URL Parameters:**
- `device_id` (required): Device identifier
- `page` (optional): Page number for pagination

**Database Operations:**
```sql
-- Get readings with pagination
SELECT * FROM iot_readings WHERE device_id = %s 
ORDER BY timestamp DESC LIMIT %s OFFSET %s

-- Get total count
SELECT COUNT(*) as total FROM iot_readings WHERE device_id = %s
```

**User Flow:** Devices List → Device Details → Edit/Delete Readings

---

### 4. Create Reading (`/create`)
**Route:** `GET /create` | `POST /create`  
**Function:** `create_reading()`  
**Template:** `templates/create.html`  
**Purpose:** Manual form to add new IoT sensor readings

**GET Request:**
- Display form for manual data entry
- Form fields: device_id, temperature, humidity, sensor_data
- Help text and JSON examples

**POST Request:**
- Validate form data
- Parse JSON sensor_data
- Insert new reading into database
- Redirect to device details on success

**Form Validation:**
- Device ID: Required, alphanumeric with underscores/hyphens
- Temperature: Optional float value
- Humidity: Optional float value (0-100%)
- Sensor Data: Optional valid JSON

**Database Operations:**
```sql
INSERT INTO iot_readings (device_id, temperature, humidity, sensor_data)
VALUES (%s, %s, %s, %s)
```

**User Flow:** Any page → Create → Device Details (of created reading)

---

### 5. Edit Reading (`/edit/<reading_id>`)
**Route:** `GET /edit/<reading_id>` | `POST /edit/<reading_id>`  
**Function:** `edit_reading(reading_id)`  
**Template:** `templates/edit.html`  
**Purpose:** Edit existing IoT sensor readings

**GET Request:**
- Retrieve existing reading data
- Pre-populate form with current values
- Show reading information (ID, timestamp, created_at)

**POST Request:**
- Validate updated form data
- Update database record
- Preserve original timestamp
- Redirect to device details

**Features:**
- Form pre-filled with existing data
- Delete option from edit page
- Timestamp preservation
- JSON validation for sensor data

**Database Operations:**
```sql
-- Get existing reading
SELECT * FROM iot_readings WHERE id = %s

-- Update reading
UPDATE iot_readings SET device_id = %s, temperature = %s, 
       humidity = %s, sensor_data = %s WHERE id = %s
```

**User Flow:** Device Details → Edit Reading → Update/Cancel → Device Details

---

### 6. Delete Reading (`/delete/<reading_id>`)
**Route:** `POST /delete/<reading_id>`  
**Function:** `delete_reading(reading_id)`  
**Purpose:** Delete specific IoT sensor reading

**Features:**
- Confirmation dialog before deletion
- Redirects to device details after deletion
- Flash message confirmation

**Database Operations:**
```sql
-- Check if reading exists
SELECT device_id FROM iot_readings WHERE id = %s

-- Delete reading
DELETE FROM iot_readings WHERE id = %s
```

**User Flow:** Device Details/Edit → Delete Confirmation → Device Details

---

### 7. Error Page (`/error`)
**Template:** `templates/error.html`  
**Purpose:** Display error messages with navigation options

**Features:**
- Error message display
- Navigation back to home or devices
- Consistent styling with main UI

---

## API Endpoints

### 1. API Home (`/api`)
**Route:** `GET /api`  
**Function:** `api_home()`  
**Purpose:** Basic API information endpoint

**Response:**
```json
{
    "message": "IoT Data Collection API",
    "status": "running", 
    "version": "1.0.0"
}
```

**Use Case:** API status check and version information

---

### 2. Receive IoT Data (`/api/data`)
**Route:** `POST /api/data`  
**Function:** `receive_iot_data()`  
**Purpose:** Primary endpoint for IoT devices to send sensor data

**Request Format:**
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

**Response (Success):**
```json
{
    "message": "Data received successfully",
    "device_id": "device_001",
    "timestamp": "2025-08-15T10:30:45"
}
```

**Validation:**
- `device_id`: Required string
- `temperature`: Optional float
- `humidity`: Optional float
- `sensor_data`: Optional JSON object

**Database Operations:**
```sql
INSERT INTO iot_readings (device_id, temperature, humidity, sensor_data)
VALUES (%s, %s, %s, %s)
```

**Use Case:** MicroPython devices, IoT sensors, automated data collection

---

### 3. Get Device Readings (`/api/data/<device_id>`)
**Route:** `GET /api/data/<device_id>`  
**Function:** `get_device_data(device_id)`  
**Purpose:** Retrieve readings for a specific device via API

**Response:**
```json
{
    "device_id": "device_001",
    "readings": [...],
    "count": 100
}
```

**Features:**
- Returns last 100 readings
- Ordered by timestamp (newest first)
- JSON format for programmatic access

**Use Case:** External applications, data analysis, monitoring dashboards

---

### 4. Health Check (`/api/health`)
**Route:** `GET /api/health`  
**Function:** `health_check()`  
**Purpose:** System and database connectivity check

**Response (Healthy):**
```json
{
    "status": "healthy",
    "database": "connected"
}
```

**Response (Unhealthy):**
```json
{
    "status": "unhealthy", 
    "database": "disconnected"
}
```

**Use Case:** Monitoring systems, load balancers, health checks

---

## CRUD API Endpoints

### 1. Create Reading (`POST /api/crud/reading`)
**Function:** `api_create_reading()`  
**Purpose:** Programmatic creation of new readings

**Request:**
```json
{
    "device_id": "esp32_001",
    "temperature": 23.5,
    "humidity": 65.2,
    "sensor_data": {"battery": 85}
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

---

### 2. Read Specific Reading (`GET /api/crud/reading/<id>`)
**Function:** `api_read_reading(reading_id)`  
**Purpose:** Get single reading by ID

**Response:**
```json
{
    "success": true,
    "reading": {
        "id": 123,
        "device_id": "esp32_001",
        "temperature": 23.5,
        "humidity": 65.2,
        "sensor_data": "{\"battery\": 85}",
        "timestamp": "2025-08-15T10:30:45",
        "created_at": "2025-08-15T10:30:45"
    }
}
```

---

### 3. Read All Readings (`GET /api/crud/readings`)
**Function:** `api_read_all_readings()`  
**Purpose:** Get paginated list of all readings

**Query Parameters:**
- `limit`: Number of results (default: 100)
- `offset`: Starting position (default: 0)

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

---

### 4. Read Device Readings (`GET /api/crud/device/<device_id>/readings`)
**Function:** `api_read_device_readings(device_id)`  
**Purpose:** Get paginated readings for specific device

**Query Parameters:**
- `limit`: Number of results (default: 100)
- `offset`: Starting position (default: 0)

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

---

### 5. Update Reading (`PUT /api/crud/reading/<id>`)
**Function:** `api_update_reading(reading_id)`  
**Purpose:** Update existing reading

**Request:**
```json
{
    "temperature": 24.1,
    "humidity": 63.8,
    "sensor_data": {"battery": 83, "updated": true}
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

---

### 6. Delete Reading (`DELETE /api/crud/reading/<id>`)
**Function:** `api_delete_reading(reading_id)`  
**Purpose:** Delete specific reading

**Response:**
```json
{
    "success": true,
    "message": "Reading 123 deleted successfully",
    "rows_affected": 1
}
```

---

### 7. Delete Device Readings (`DELETE /api/crud/device/<device_id>`)
**Function:** `api_delete_device_readings(device_id)`  
**Purpose:** Delete all readings for a device

**Response:**
```json
{
    "success": true,
    "message": "Deleted 45 readings for device esp32_001",
    "rows_affected": 45
}
```

---

## Database Operations

### IoTDataCRUD Class Methods

#### `create_reading(device_id, temperature, humidity, sensor_data)`
**Purpose:** Insert new reading into database  
**Returns:** Success status and reading ID

#### `read_reading(reading_id)`
**Purpose:** Fetch single reading by ID  
**Returns:** Reading data or error

#### `read_all_readings(limit, offset)`
**Purpose:** Fetch paginated list of all readings  
**Returns:** Readings array with pagination info

#### `read_device_readings(device_id, limit, offset)`
**Purpose:** Fetch paginated readings for specific device  
**Returns:** Device readings with pagination info

#### `update_reading(reading_id, **kwargs)`
**Purpose:** Update existing reading with provided fields  
**Returns:** Success status and affected rows

#### `delete_reading(reading_id)`
**Purpose:** Remove single reading from database  
**Returns:** Success status and affected rows

#### `delete_device_readings(device_id)`
**Purpose:** Remove all readings for a device  
**Returns:** Success status and count deleted

---

## Database Schema

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

**Indexes:**
- Primary key on `id`
- Index on `device_id` for device queries
- Index on `timestamp` for time-based queries

---

## Error Handling

### Web Interface Errors
- **Flash Messages:** User-friendly Thai error messages
- **Form Validation:** Client-side and server-side validation
- **Database Errors:** Graceful fallback with error page
- **404 Errors:** Redirect to appropriate pages

### API Errors
- **400 Bad Request:** Invalid data format or missing required fields
- **404 Not Found:** Reading or device not found
- **500 Internal Server Error:** Database connection issues
- **503 Service Unavailable:** Database unavailable

### Error Response Format
```json
{
    "success": false,
    "error": "Error description"
}
```

---

## Security Considerations

### Input Validation
- JSON parsing with error handling
- SQL injection prevention using parameterized queries
- XSS prevention in templates
- CSRF protection with Flask's built-in features

### Database Security
- Connection parameters validation
- Error message sanitization
- Transaction rollback on errors

### Rate Limiting
- Consider implementing for production use
- Especially for API endpoints receiving IoT data

---

## Performance Optimization

### Database Queries
- Pagination for large datasets
- Indexes on frequently queried columns
- Connection pooling for high traffic

### Caching
- Static file caching for CSS/JS
- Template caching for repeated renders
- API response caching for read-heavy operations

### Monitoring
- Health check endpoint for system monitoring
- Database connection monitoring
- Error logging and alerting

---

This documentation covers all endpoints and pages in the Flask IoT Data Management System, providing developers and users with comprehensive understanding of the system's functionality and usage patterns.
