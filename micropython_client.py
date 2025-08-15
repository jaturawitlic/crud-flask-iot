# Example MicroPython script for ESP32/ESP8266
# This script connects to WiFi and sends sensor data to the Flask API

import urequests
import json
import network
import time
from machine import Pin, ADC
import dht

# WiFi configuration
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"

# API configuration
API_URL = "http://your_server_ip:5001/api/data"
DEVICE_ID = "esp32_001"

# Sensor configuration (adjust pins as needed)
# DHT22 sensor for temperature and humidity
dht_sensor = dht.DHT22(Pin(4))

# Light sensor (LDR) connected to ADC
light_sensor = ADC(Pin(36))
light_sensor.atten(ADC.ATTN_11DB)

def connect_wifi():
    """Connect to WiFi network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        while not wlan.isconnected():
            print(".", end="")
            time.sleep(1)
    
    print("\nWiFi connected!")
    print("Network config:", wlan.ifconfig())

def read_sensors():
    """Read data from connected sensors"""
    sensor_data = {}
    
    try:
        # Read DHT22 sensor
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        
        # Read light sensor (convert to percentage)
        light_raw = light_sensor.read()
        light_percentage = (light_raw / 4095) * 100
        
        sensor_data = {
            "temperature": temperature,
            "humidity": humidity,
            "light": round(light_percentage, 2),
            "light_raw": light_raw
        }
        
        print("Sensor readings:", sensor_data)
        return sensor_data
        
    except Exception as e:
        print("Error reading sensors:", e)
        return {
            "temperature": None,
            "humidity": None,
            "light": None,
            "error": str(e)
        }

def send_sensor_data(sensor_data):
    """Send sensor data to Flask API"""
    data = {
        "device_id": DEVICE_ID,
        "temperature": sensor_data.get("temperature"),
        "humidity": sensor_data.get("humidity"),
        "sensor_data": {
            "light": sensor_data.get("light"),
            "light_raw": sensor_data.get("light_raw"),
            "timestamp": time.time()
        }
    }
    
    try:
        headers = {'Content-Type': 'application/json'}
        print("Sending data to API...")
        
        response = urequests.post(
            API_URL, 
            data=json.dumps(data), 
            headers=headers
        )
        
        print("Response Status:", response.status_code)
        if response.status_code == 201:
            print("Data sent successfully!")
        else:
            print("Server response:", response.text)
        
        response.close()
        return True
        
    except Exception as e:
        print("Error sending data:", e)
        return False

def main_loop():
    """Main execution loop"""
    print("Starting IoT data collection...")
    
    # Connect to WiFi
    connect_wifi()
    
    # Main loop - send data every 30 seconds
    while True:
        try:
            print("\n--- Reading sensors ---")
            
            # Read sensor data
            sensor_data = read_sensors()
            
            # Send to API
            success = send_sensor_data(sensor_data)
            
            if success:
                print("Data transmission completed")
            else:
                print("Data transmission failed")
            
            # Wait before next reading
            print("Waiting 30 seconds...")
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\nProgram stopped by user")
            break
        except Exception as e:
            print("Unexpected error:", e)
            time.sleep(5)  # Wait before retrying

# Run the main loop
if __name__ == "__main__":
    main_loop()
