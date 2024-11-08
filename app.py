from flask import Flask, jsonify, request
import psycopg2
import os
from dotenv import load_dotenv

#Load environment variables
load_dotenv()

app = Flask(__name__)

def get_db_connection():
    connection = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return connection

@app.route('/equipment', methods=['GET'])
def get_equipment():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM equipment;')
    equipment = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert result to JSON format
    equipment_list = [
        {"id": row[0], "type": row[1], "model": row[2], "daily_rate": row[3], "weekly_rate": row[4], "monthly_rate": row[5], "location": row[6]}
        for row in equipment
    ]

    return jsonify(equipment_list)

@app.route('/equipment/<int:id>', methods=['GET'])
def get_equipment_by_id(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM equipment WHERE id = %s;', (id,))
    equipment = cursor.fetchone()
    cursor.close()
    conn.close()

    if equipment is None:
        return jsonify({'error': 'Equipment not found'}), 404

    equipment_data = {
        "id": equipment[0],
        "type": equipment[1],
        "model": equipment[2],
        "daily_rate": equipment[3],
        "weekly_rate": equipment[4],
        "monthly_rate": equipment[5],
        "location": equipment[6]
    }

    return jsonify(equipment_data)

@app.route('/estimate', methods=['POST'])
def estimate_cost():
    data = request.json
    equipment_type = data.get('type')
    rental_duration = data.get('duration')
    rental_unit = data.get('unit', 'daily')  # Default to daily rate if not specified

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT daily_rate, weekly_rate, monthly_rate FROM equipment WHERE type = %s;', (equipment_type,))
    rate = cursor.fetchone()
    cursor.close()
    conn.close()

    if rate is None:
        return jsonify({'error': 'Equipment type not found'}), 404

    # Determine cost based on rental unit
    if rental_unit == 'daily':
        estimated_cost = rate[0] * rental_duration
    elif rental_unit == 'weekly':
        estimated_cost = rate[1] * rental_duration
    elif rental_unit == 'monthly':
        estimated_cost = rate[2] * rental_duration
    else:
        return jsonify({'error': 'Invalid rental unit'}), 400

    return jsonify({
        'equipment_type': equipment_type,
        'rental_duration': rental_duration,
        'rental_unit': rental_unit,
        'estimated_cost': estimated_cost
    })
