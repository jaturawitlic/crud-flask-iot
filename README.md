# IoT Data Collection API with Flask

A Flask-based REST API for collecting data from IoT devices using MicroPython, with MySQL database storage.

## Features

- RESTful API for receiving IoT sensor data
- MySQL database integration
- Device-specific data retrieval
- Health check endpoint
- JSON data format support

## Database Configuration

The application connects to your MySQL database with the following configuration:
- **Host**: 61.19.114.86:54000
- **User**: nathee
- **Database**: iot_data

## API Endpoints

### 1. Home
- **URL**: `/`
- **Method**: GET
- **Description**: Basic API information

### 2. Receive IoT Data
- **URL**: `/api/data`
- **Method**: POST
- **Content-Type**: application/json
- **Body Example**:
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

### 3. Get Device Data
- **URL**: `/api/data/<device_id>`
- **Method**: GET
- **Description**: Retrieve last 100 readings for a specific device

### 4. Health Check
- **URL**: `/api/health`
- **Method**: GET
- **Description**: Check API and database connectivity

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:5001`

## MicroPython Client Example

Here's a basic MicroPython script to send data to your Flask API:

```python
import urequests
import json
import network
import time

# WiFi configuration
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"

# API configuration
API_URL = "http://your_server_ip:5001/api/data"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    while not wlan.isconnected():
        time.sleep(1)
    
    print("WiFi connected:", wlan.ifconfig())

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
        
        print("Response:", response.status_code, response.text)
        response.close()
        
    except Exception as e:
        print("Error sending data:", e)

# Main execution
if __name__ == "__main__":
    connect_wifi()
    
    # Send sample data
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

## Database Schema

The application creates a table called `iot_readings` with the following structure:

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

## Development

- The application runs in debug mode by default
- Database tables are created automatically on first run
- Check `/api/health` to verify database connectivity

## Security Notes

- Consider implementing authentication for production use
- Validate and sanitize input data
- Use environment variables for sensitive configuration
- Implement rate limiting for API endpoints
