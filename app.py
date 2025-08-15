from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import json

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': '61.19.114.86',
    'port': 54000,
    'user': 'nathee',
    'password': 'Root@1234',
    'database': 'iot_data'  # You may need to create this database
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_database():
    """Initialize the database and create tables if they don't exist"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS iot_data")
            cursor.execute("USE iot_data")
            
            # Create iot_readings table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS iot_readings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                device_id VARCHAR(100) NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sensor_data JSON,
                temperature FLOAT,
                humidity FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            connection.commit()
            print("Database and table created successfully")
            
        except Error as e:
            print(f"Error initializing database: {e}")
        finally:
            cursor.close()
            connection.close()

@app.route('/')
def home():
    """Basic home endpoint"""
    return jsonify({
        "message": "IoT Data Collection API",
        "status": "running",
        "version": "1.0.0"
    })

@app.route('/api/data', methods=['POST'])
def receive_iot_data():
    """
    Endpoint to receive data from IoT devices
    Expected JSON format:
    {
        "device_id": "device_001",
        "temperature": 25.5,
        "humidity": 60.2,
        "sensor_data": {...}
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        # Extract required fields
        device_id = data.get('device_id')
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        sensor_data = data.get('sensor_data', {})
        
        if not device_id:
            return jsonify({"error": "device_id is required"}), 400
        
        # Connect to database
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500
        
        try:
            cursor = connection.cursor()
            
            # Insert data into database
            insert_query = """
            INSERT INTO iot_readings (device_id, temperature, humidity, sensor_data)
            VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                device_id,
                temperature,
                humidity,
                json.dumps(sensor_data)
            ))
            
            connection.commit()
            
            return jsonify({
                "message": "Data received successfully",
                "device_id": device_id,
                "timestamp": datetime.now().isoformat()
            }), 201
            
        except Error as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        
        finally:
            cursor.close()
            connection.close()
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/data/<device_id>', methods=['GET'])
def get_device_data(device_id):
    """Get data for a specific device"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            query = """
            SELECT * FROM iot_readings 
            WHERE device_id = %s 
            ORDER BY timestamp DESC 
            LIMIT 100
            """
            
            cursor.execute(query, (device_id,))
            readings = cursor.fetchall()
            
            return jsonify({
                "device_id": device_id,
                "readings": readings,
                "count": len(readings)
            })
            
        except Error as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        
        finally:
            cursor.close()
            connection.close()
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        connection = get_db_connection()
        if connection:
            connection.close()
            return jsonify({"status": "healthy", "database": "connected"})
        else:
            return jsonify({"status": "unhealthy", "database": "disconnected"}), 503
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
