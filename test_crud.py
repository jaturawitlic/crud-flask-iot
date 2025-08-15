#!/usr/bin/env python3
"""
Test script for basic CRUD operations to std01_iot_data database
Run this script to test all CRUD functionality
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://127.0.0.1:5001"
API_URL = f"{BASE_URL}/api/crud"

def print_section(title):
    """Print a section header"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def print_response(response, operation):
    """Print API response in a formatted way"""
    try:
        data = response.json()
        print(f"{operation}: {response.status_code}")
        print(json.dumps(data, indent=2))
        return data
    except:
        print(f"{operation}: {response.status_code} - {response.text}")
        return None

def test_crud_operations():
    """Test all CRUD operations"""
    
    print_section("TESTING BASIC CRUD OPERATIONS TO std01_iot_data DATABASE")
    
    # ========================
    # CREATE - Add new readings
    # ========================
    print_section("1. CREATE - Adding New Readings")
    
    # Create first reading
    reading1_data = {
        "device_id": "test_device_001",
        "temperature": 23.5,
        "humidity": 65.2,
        "sensor_data": {
            "light": 750,
            "pressure": 1013.25,
            "battery": 85
        }
    }
    
    response = requests.post(f"{API_URL}/reading", json=reading1_data)
    result1 = print_response(response, "Create Reading 1")
    reading1_id = result1.get('reading_id') if result1 and result1.get('success') else None
    
    # Create second reading
    reading2_data = {
        "device_id": "test_device_002",
        "temperature": 28.7,
        "humidity": 58.9,
        "sensor_data": {
            "light": 820,
            "motion": True,
            "battery": 92
        }
    }
    
    response = requests.post(f"{API_URL}/reading", json=reading2_data)
    result2 = print_response(response, "Create Reading 2")
    reading2_id = result2.get('reading_id') if result2 and result2.get('success') else None
    
    # Create third reading for same device
    reading3_data = {
        "device_id": "test_device_001",
        "temperature": 24.1,
        "humidity": 63.8,
        "sensor_data": {
            "light": 780,
            "pressure": 1012.1,
            "battery": 83
        }
    }
    
    response = requests.post(f"{API_URL}/reading", json=reading3_data)
    result3 = print_response(response, "Create Reading 3")
    reading3_id = result3.get('reading_id') if result3 and result3.get('success') else None
    
    time.sleep(1)  # Wait a moment between operations
    
    # ========================
    # READ - Get readings
    # ========================
    print_section("2. READ - Retrieving Readings")
    
    if reading1_id:
        # Read specific reading
        response = requests.get(f"{API_URL}/reading/{reading1_id}")
        print_response(response, f"Read Reading {reading1_id}")
    
    # Read all readings
    response = requests.get(f"{API_URL}/readings?limit=10")
    print_response(response, "Read All Readings (limit 10)")
    
    # Read device-specific readings
    response = requests.get(f"{API_URL}/device/test_device_001/readings")
    print_response(response, "Read test_device_001 Readings")
    
    time.sleep(1)
    
    # ========================
    # UPDATE - Modify readings
    # ========================
    print_section("3. UPDATE - Modifying Readings")
    
    if reading2_id:
        update_data = {
            "temperature": 29.5,
            "humidity": 55.0,
            "sensor_data": {
                "light": 900,
                "motion": False,
                "battery": 90,
                "updated": True
            }
        }
        
        response = requests.put(f"{API_URL}/reading/{reading2_id}", json=update_data)
        print_response(response, f"Update Reading {reading2_id}")
        
        # Verify update by reading it back
        response = requests.get(f"{API_URL}/reading/{reading2_id}")
        print_response(response, f"Verify Update - Read Reading {reading2_id}")
    
    time.sleep(1)
    
    # ========================
    # READ - Get updated data
    # ========================
    print_section("4. READ - After Updates")
    
    # Read all readings again to see changes
    response = requests.get(f"{API_URL}/readings?limit=5")
    print_response(response, "Read All Readings After Update")
    
    time.sleep(1)
    
    # ========================
    # DELETE - Remove readings
    # ========================
    print_section("5. DELETE - Removing Readings")
    
    if reading3_id:
        # Delete specific reading
        response = requests.delete(f"{API_URL}/reading/{reading3_id}")
        print_response(response, f"Delete Reading {reading3_id}")
        
        # Verify deletion
        response = requests.get(f"{API_URL}/reading/{reading3_id}")
        print_response(response, f"Verify Deletion - Try to Read {reading3_id}")
    
    # Delete all readings for a device
    response = requests.delete(f"{API_URL}/device/test_device_001")
    print_response(response, "Delete All Readings for test_device_001")
    
    time.sleep(1)
    
    # ========================
    # FINAL READ - Check remaining data
    # ========================
    print_section("6. FINAL READ - Check Remaining Data")
    
    response = requests.get(f"{API_URL}/readings")
    final_result = print_response(response, "Final Read - All Remaining Readings")
    
    # Clean up remaining test data
    if final_result and final_result.get('success'):
        remaining_readings = final_result.get('readings', [])
        print(f"\nCleaning up {len(remaining_readings)} remaining test readings...")
        
        for reading in remaining_readings:
            if reading['device_id'].startswith('test_device_'):
                response = requests.delete(f"{API_URL}/reading/{reading['id']}")
                print(f"Cleaned up reading {reading['id']}: {response.status_code}")
    
    print_section("CRUD OPERATIONS TEST COMPLETED")
    print("All basic CRUD operations have been tested!")
    print(f"\nYou can also test the web interface at: {BASE_URL}")

if __name__ == "__main__":
    try:
        test_crud_operations()
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Flask server!")
        print("Make sure the Flask app is running on http://127.0.0.1:5001")
        print("Run: python app.py")
    except Exception as e:
        print(f"ERROR: {e}")
