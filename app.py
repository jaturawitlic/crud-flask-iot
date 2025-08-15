from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

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
    """Home page with navigation to CRUD operations"""
    return render_template('index.html')

@app.route('/api')
def api_home():
    """Basic API information endpoint"""
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

# Web CRUD Routes
@app.route('/devices')
def list_devices():
    """Display all devices and their latest readings"""
    try:
        connection = get_db_connection()
        if not connection:
            flash("Database connection failed", "error")
            return render_template('error.html', error="Database connection failed")
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get all devices with their latest reading
            query = """
            SELECT 
                device_id,
                MAX(timestamp) as last_seen,
                COUNT(*) as total_readings,
                AVG(temperature) as avg_temperature,
                AVG(humidity) as avg_humidity
            FROM iot_readings 
            GROUP BY device_id 
            ORDER BY last_seen DESC
            """
            
            cursor.execute(query)
            devices = cursor.fetchall()
            
            return render_template('devices.html', devices=devices)
            
        except Error as e:
            flash(f"Database error: {str(e)}", "error")
            return render_template('error.html', error=str(e))
        
        finally:
            cursor.close()
            connection.close()
    
    except Exception as e:
        flash(f"Server error: {str(e)}", "error")
        return render_template('error.html', error=str(e))

@app.route('/device/<device_id>')
def view_device(device_id):
    """View detailed readings for a specific device"""
    try:
        connection = get_db_connection()
        if not connection:
            flash("Database connection failed", "error")
            return render_template('error.html', error="Database connection failed")
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get device readings with pagination
            page = request.args.get('page', 1, type=int)
            per_page = 20
            offset = (page - 1) * per_page
            
            # Get readings
            query = """
            SELECT * FROM iot_readings 
            WHERE device_id = %s 
            ORDER BY timestamp DESC 
            LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, (device_id, per_page, offset))
            readings = cursor.fetchall()
            
            # Get total count
            count_query = "SELECT COUNT(*) as total FROM iot_readings WHERE device_id = %s"
            cursor.execute(count_query, (device_id,))
            total = cursor.fetchone()['total']
            
            # Calculate pagination info
            total_pages = (total + per_page - 1) // per_page
            has_prev = page > 1
            has_next = page < total_pages
            
            return render_template('device_detail.html', 
                                 device_id=device_id,
                                 readings=readings,
                                 page=page,
                                 total_pages=total_pages,
                                 has_prev=has_prev,
                                 has_next=has_next,
                                 total=total)
            
        except Error as e:
            flash(f"Database error: {str(e)}", "error")
            return render_template('error.html', error=str(e))
        
        finally:
            cursor.close()
            connection.close()
    
    except Exception as e:
        flash(f"Server error: {str(e)}", "error")
        return render_template('error.html', error=str(e))

@app.route('/create', methods=['GET', 'POST'])
def create_reading():
    """Create new IoT reading manually"""
    if request.method == 'GET':
        return render_template('create.html')
    
    try:
        # Get form data
        device_id = request.form.get('device_id')
        temperature = request.form.get('temperature')
        humidity = request.form.get('humidity')
        sensor_data_str = request.form.get('sensor_data', '{}')
        
        if not device_id:
            flash("Device ID is required", "error")
            return render_template('create.html')
        
        # Parse sensor data JSON
        try:
            sensor_data = json.loads(sensor_data_str) if sensor_data_str else {}
        except json.JSONDecodeError:
            flash("Invalid JSON format in sensor data", "error")
            return render_template('create.html')
        
        # Convert temperature and humidity to float
        try:
            temperature = float(temperature) if temperature else None
            humidity = float(humidity) if humidity else None
        except ValueError:
            flash("Temperature and humidity must be valid numbers", "error")
            return render_template('create.html')
        
        # Connect to database
        connection = get_db_connection()
        if not connection:
            flash("Database connection failed", "error")
            return render_template('create.html')
        
        try:
            cursor = connection.cursor()
            
            # Insert data
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
            flash(f"Reading created successfully for device {device_id}", "success")
            return redirect(url_for('view_device', device_id=device_id))
            
        except Error as e:
            flash(f"Database error: {str(e)}", "error")
            return render_template('create.html')
        
        finally:
            cursor.close()
            connection.close()
    
    except Exception as e:
        flash(f"Server error: {str(e)}", "error")
        return render_template('create.html')

@app.route('/edit/<int:reading_id>', methods=['GET', 'POST'])
def edit_reading(reading_id):
    """Edit an existing IoT reading"""
    connection = get_db_connection()
    if not connection:
        flash("Database connection failed", "error")
        return redirect(url_for('list_devices'))
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        if request.method == 'GET':
            # Get the reading to edit
            query = "SELECT * FROM iot_readings WHERE id = %s"
            cursor.execute(query, (reading_id,))
            reading = cursor.fetchone()
            
            if not reading:
                flash("Reading not found", "error")
                return redirect(url_for('list_devices'))
            
            return render_template('edit.html', reading=reading)
        
        else:  # POST method
            # Update the reading
            device_id = request.form.get('device_id')
            temperature = request.form.get('temperature')
            humidity = request.form.get('humidity')
            sensor_data_str = request.form.get('sensor_data', '{}')
            
            if not device_id:
                flash("Device ID is required", "error")
                return redirect(url_for('edit_reading', reading_id=reading_id))
            
            # Parse sensor data JSON
            try:
                sensor_data = json.loads(sensor_data_str) if sensor_data_str else {}
            except json.JSONDecodeError:
                flash("Invalid JSON format in sensor data", "error")
                return redirect(url_for('edit_reading', reading_id=reading_id))
            
            # Convert temperature and humidity to float
            try:
                temperature = float(temperature) if temperature else None
                humidity = float(humidity) if humidity else None
            except ValueError:
                flash("Temperature and humidity must be valid numbers", "error")
                return redirect(url_for('edit_reading', reading_id=reading_id))
            
            # Update query
            update_query = """
            UPDATE iot_readings 
            SET device_id = %s, temperature = %s, humidity = %s, sensor_data = %s
            WHERE id = %s
            """
            
            cursor.execute(update_query, (
                device_id,
                temperature,
                humidity,
                json.dumps(sensor_data),
                reading_id
            ))
            
            connection.commit()
            flash("Reading updated successfully", "success")
            return redirect(url_for('view_device', device_id=device_id))
            
    except Error as e:
        flash(f"Database error: {str(e)}", "error")
        return redirect(url_for('list_devices'))
    
    finally:
        cursor.close()
        connection.close()

@app.route('/delete/<int:reading_id>', methods=['POST'])
def delete_reading(reading_id):
    """Delete an IoT reading"""
    try:
        connection = get_db_connection()
        if not connection:
            flash("Database connection failed", "error")
            return redirect(url_for('list_devices'))
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get the reading to check device_id before deletion
            query = "SELECT device_id FROM iot_readings WHERE id = %s"
            cursor.execute(query, (reading_id,))
            reading = cursor.fetchone()
            
            if not reading:
                flash("Reading not found", "error")
                return redirect(url_for('list_devices'))
            
            device_id = reading['device_id']
            
            # Delete the reading
            delete_query = "DELETE FROM iot_readings WHERE id = %s"
            cursor.execute(delete_query, (reading_id,))
            connection.commit()
            
            flash("Reading deleted successfully", "success")
            return redirect(url_for('view_device', device_id=device_id))
            
        except Error as e:
            flash(f"Database error: {str(e)}", "error")
            return redirect(url_for('list_devices'))
        
        finally:
            cursor.close()
            connection.close()
    
    except Exception as e:
        flash(f"Server error: {str(e)}", "error")
        return redirect(url_for('list_devices'))

# ========================
# BASIC CRUD OPERATIONS TO iot_data DATABASE
# ========================

class IoTDataCRUD:
    """Basic CRUD operations for iot_data database"""
    
    @staticmethod
    def create_reading(device_id, temperature=None, humidity=None, sensor_data=None):
        """Create a new reading in the database"""
        connection = get_db_connection()
        if not connection:
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO iot_readings (device_id, temperature, humidity, sensor_data)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (
                device_id,
                temperature,
                humidity,
                json.dumps(sensor_data) if sensor_data else None
            ))
            connection.commit()
            reading_id = cursor.lastrowid
            
            return {
                "success": True, 
                "reading_id": reading_id,
                "message": f"Reading created with ID {reading_id}"
            }
            
        except Error as e:
            return {"success": False, "error": f"Database error: {str(e)}"}
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def read_reading(reading_id):
        """Read a specific reading from the database"""
        connection = get_db_connection()
        if not connection:
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM iot_readings WHERE id = %s"
            cursor.execute(query, (reading_id,))
            reading = cursor.fetchone()
            
            if reading:
                return {"success": True, "reading": reading}
            else:
                return {"success": False, "error": "Reading not found"}
                
        except Error as e:
            return {"success": False, "error": f"Database error: {str(e)}"}
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def read_all_readings(limit=100, offset=0):
        """Read all readings from the database with pagination"""
        connection = get_db_connection()
        if not connection:
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get readings with pagination
            query = """
            SELECT * FROM iot_readings 
            ORDER BY timestamp DESC 
            LIMIT %s OFFSET %s
            """
            cursor.execute(query, (limit, offset))
            readings = cursor.fetchall()
            
            # Get total count
            count_query = "SELECT COUNT(*) as total FROM iot_readings"
            cursor.execute(count_query)
            total = cursor.fetchone()['total']
            
            return {
                "success": True,
                "readings": readings,
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Error as e:
            return {"success": False, "error": f"Database error: {str(e)}"}
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def read_device_readings(device_id, limit=100, offset=0):
        """Read all readings for a specific device"""
        connection = get_db_connection()
        if not connection:
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get readings for specific device
            query = """
            SELECT * FROM iot_readings 
            WHERE device_id = %s 
            ORDER BY timestamp DESC 
            LIMIT %s OFFSET %s
            """
            cursor.execute(query, (device_id, limit, offset))
            readings = cursor.fetchall()
            
            # Get total count for this device
            count_query = "SELECT COUNT(*) as total FROM iot_readings WHERE device_id = %s"
            cursor.execute(count_query, (device_id,))
            total = cursor.fetchone()['total']
            
            return {
                "success": True,
                "device_id": device_id,
                "readings": readings,
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Error as e:
            return {"success": False, "error": f"Database error: {str(e)}"}
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def update_reading(reading_id, device_id=None, temperature=None, humidity=None, sensor_data=None):
        """Update an existing reading in the database"""
        connection = get_db_connection()
        if not connection:
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = connection.cursor()
            
            # Check if reading exists
            cursor.execute("SELECT id FROM iot_readings WHERE id = %s", (reading_id,))
            if not cursor.fetchone():
                return {"success": False, "error": "Reading not found"}
            
            # Build dynamic update query
            update_parts = []
            params = []
            
            if device_id is not None:
                update_parts.append("device_id = %s")
                params.append(device_id)
            if temperature is not None:
                update_parts.append("temperature = %s")
                params.append(temperature)
            if humidity is not None:
                update_parts.append("humidity = %s")
                params.append(humidity)
            if sensor_data is not None:
                update_parts.append("sensor_data = %s")
                params.append(json.dumps(sensor_data))
            
            if not update_parts:
                return {"success": False, "error": "No fields to update"}
            
            query = f"UPDATE iot_readings SET {', '.join(update_parts)} WHERE id = %s"
            params.append(reading_id)
            
            cursor.execute(query, params)
            connection.commit()
            
            return {
                "success": True,
                "message": f"Reading {reading_id} updated successfully",
                "rows_affected": cursor.rowcount
            }
            
        except Error as e:
            return {"success": False, "error": f"Database error: {str(e)}"}
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def delete_reading(reading_id):
        """Delete a reading from the database"""
        connection = get_db_connection()
        if not connection:
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = connection.cursor()
            
            # Check if reading exists first
            cursor.execute("SELECT id FROM iot_readings WHERE id = %s", (reading_id,))
            if not cursor.fetchone():
                return {"success": False, "error": "Reading not found"}
            
            # Delete the reading
            query = "DELETE FROM iot_readings WHERE id = %s"
            cursor.execute(query, (reading_id,))
            connection.commit()
            
            return {
                "success": True,
                "message": f"Reading {reading_id} deleted successfully",
                "rows_affected": cursor.rowcount
            }
            
        except Error as e:
            return {"success": False, "error": f"Database error: {str(e)}"}
        finally:
            cursor.close()
            connection.close()
    
    @staticmethod
    def delete_device_readings(device_id):
        """Delete all readings for a specific device"""
        connection = get_db_connection()
        if not connection:
            return {"success": False, "error": "Database connection failed"}
        
        try:
            cursor = connection.cursor()
            
            # Count readings before deletion
            cursor.execute("SELECT COUNT(*) as count FROM iot_readings WHERE device_id = %s", (device_id,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                return {"success": False, "error": f"No readings found for device {device_id}"}
            
            # Delete all readings for the device
            query = "DELETE FROM iot_readings WHERE device_id = %s"
            cursor.execute(query, (device_id,))
            connection.commit()
            
            return {
                "success": True,
                "message": f"Deleted {count} readings for device {device_id}",
                "rows_affected": cursor.rowcount
            }
            
        except Error as e:
            return {"success": False, "error": f"Database error: {str(e)}"}
        finally:
            cursor.close()
            connection.close()

# ========================
# CRUD API ENDPOINTS
# ========================

@app.route('/api/crud/reading', methods=['POST'])
def api_create_reading():
    """API endpoint to create a new reading"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        result = IoTDataCRUD.create_reading(
            device_id=data.get('device_id'),
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            sensor_data=data.get('sensor_data')
        )
        
        status_code = 201 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/crud/reading/<int:reading_id>', methods=['GET'])
def api_read_reading(reading_id):
    """API endpoint to read a specific reading"""
    try:
        result = IoTDataCRUD.read_reading(reading_id)
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/crud/readings', methods=['GET'])
def api_read_all_readings():
    """API endpoint to read all readings with pagination"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        result = IoTDataCRUD.read_all_readings(limit=limit, offset=offset)
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/crud/device/<device_id>/readings', methods=['GET'])
def api_read_device_readings(device_id):
    """API endpoint to read all readings for a specific device"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        result = IoTDataCRUD.read_device_readings(device_id, limit=limit, offset=offset)
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/crud/reading/<int:reading_id>', methods=['PUT'])
def api_update_reading(reading_id):
    """API endpoint to update a specific reading"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        result = IoTDataCRUD.update_reading(
            reading_id=reading_id,
            device_id=data.get('device_id'),
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            sensor_data=data.get('sensor_data')
        )
        
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/crud/reading/<int:reading_id>', methods=['DELETE'])
def api_delete_reading(reading_id):
    """API endpoint to delete a specific reading"""
    try:
        result = IoTDataCRUD.delete_reading(reading_id)
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/crud/device/<device_id>', methods=['DELETE'])
def api_delete_device_readings(device_id):
    """API endpoint to delete all readings for a specific device"""
    try:
        result = IoTDataCRUD.delete_device_readings(device_id)
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
