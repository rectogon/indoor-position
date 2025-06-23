from flask import Flask, jsonify ,request
import psycopg2
from psycopg2 import Error
import os
app = Flask(__name__)
setTrue = True

# PostgreSQL configuration
db_config_Anchor = {
    'dbname': 'BLE',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}

# Function to connect to the PostgreSQL database
def connect_db_Anchor():
    return psycopg2.connect(**db_config_Anchor)

# Flask for Anchor
@app.route('/Verify', methods=['GET']) # Login verification
def verify_login():
    try:
        conn = connect_db_Anchor()
        cur = conn.cursor()

        # Get the anchor from the request parameters
        name = request.args.get('anc_name')

        query = "SELECT anc_no, anc_name, rssi, timestamp FROM rssi_test_01"
        cur.execute(query, (name, ))

        user = cur.fetchall()

        if user:
            results = []
            for u in user:
                result = {
                        'Anchor name': u[1],
                        'RSSI': u[2],
                        'No.': u[0],
                        'Timestamp': u[3]
                        }
                results.append(result)
            
        else:
            results = ['Data not found']

        return jsonify(results)

    except (Exception, Error) as error:
        print("Error connecting to the database:", error)
        return jsonify({'error': str(error)})

    finally:
        cur.close()
        conn.close()
        
        
@app.route('/Table_Point', methods=['GET'])
def Table_PointA():
    try:
        conn = connect_db_Anchor()
        cur = conn.cursor()

        # รับค่า ip จาก request
        point = request.args.get('point')
        if not point:
            return jsonify({'error': 'Missing IP parameter'}), 400

        # ดึง point_id จาก IP
        cur.execute("SELECT point_id FROM rssi_data WHERE point_id = %s", (point,))
        point_data = cur.fetchone()
        
        if not point_data:
            return jsonify({'error': 'IP not found in database'}), 404

        point_id = point_data[0]  # ดึงค่า point_id ออกมาใช้

        # Query เพื่อดึงข้อมูลทั้งหมดที่เกี่ยวข้องกับ point_id นี้
        query = """
            SELECT rd.point_id, 
                   pa.x, pa.y, pa.error_distance, 
                   pr.x, pr.y, pr.error_distance
            FROM rssi_data rd
            LEFT JOIN position_aoa pa ON rd.id = pa.rssi_data_id
            LEFT JOIN position_rssi pr ON rd.id = pr.rssi_data_id
            WHERE rd.point_id = %s
        """
        
        cur.execute(query, (point_id,))
        data = cur.fetchall()

        results = []
        if data:
            for row in data:
                result = {
                    'Point': row[0],
                    'X_AoA': row[1],
                    'Y_AoA': row[2],
                    'Error_AoA': row[3],
                    'X_RSSI': row[4],
                    'Y_RSSI': row[5],
                    'Error_RSSI': row[6]
                }
                results.append(result)
        else:
            results = ['Data not found']

        return jsonify(results)

    except (Exception, Error) as error:
        print("Error connecting to the database:", error)
        return jsonify({'error': str(error)})

    finally:
        cur.close()
        conn.close()
        
        
@app.route('/rssi_data', methods=['POST']) # send data
def rssi_data():
    try:
        conn = connect_db_Anchor()
        cur = conn.cursor()

        # Get the name and rssi from the request parameters
        data = request.get_json()

        point = data.get('point')
        
        cur.execute("INSERT INTO rssi_data(point_id, timestamp) VALUES (%s, to_timestamp(to_char(now(), 'YYYY-MM-DD HH24:MI:SS'), 'YYYY-MM-DD HH24:MI:SS'))", (point,))
        conn.commit()

        return jsonify({"message": "Data inserted successfully."}), 200
    
    except (Exception, Error) as error:
        print("Error connecting to the database:", error)
        return jsonify({'error': str(error)})

    finally:
        cur.close()
        conn.close()
        

@app.route('/rssi_data_list', methods=['POST']) # send data
def rssi_data_list():
    try:
        conn = connect_db_Anchor()
        cur = conn.cursor()

        # Get the name and rssi from the request parameters
        data = request.get_json()

        rssi = data.get('rssi')
        anchor_id = data.get('anchor_id')
        
        cur.execute("SELECT id FROM rssi_data ORDER BY id DESC LIMIT 1")
        rssi_id = cur.fetchone()[0]  # ดึงค่าเดียวออกมา

        cur.execute("INSERT INTO rssi_data_list(rssi_data_id, anchor_id, rssi_value, timestamp) VALUES (%s, %s, %s, to_timestamp(to_char(now(), 'YYYY-MM-DD HH24:MI:SS'), 'YYYY-MM-DD HH24:MI:SS'))", (rssi_id, anchor_id, rssi,))
        conn.commit()

        return jsonify({"message": "Data inserted successfully."}), 200
    
    except (Exception, Error) as error:
        print("Error connecting to the database:", error)
        return jsonify({'error': str(error)})

    finally:
        cur.close()
        conn.close()
        
        
@app.route('/position_aoa', methods=['POST']) # send data
def insert_aoa():
    try:
        conn = connect_db_Anchor()
        cur = conn.cursor()

        # Get the name and rssi from the request parameters
        data = request.get_json()
    
        x = data.get('x')
        y = data.get('y')
        error = data.get('error')
        status = data.get('status')
        
        cur.execute("SELECT id FROM rssi_data ORDER BY id DESC LIMIT 1")
        rssi_id = cur.fetchone()[0]  # ดึงค่าเดียวออกมา
        
        cur.execute("INSERT INTO position_aoa(rssi_data_id, x, y, error_distance, status, timestamp) VALUES (%s, %s, %s, %s, %s, to_timestamp(to_char(now(), 'YYYY-MM-DD HH24:MI:SS'), 'YYYY-MM-DD HH24:MI:SS'))", (rssi_id, x, y, error, status,))
        conn.commit()

        return jsonify({"message": "Data inserted successfully."}), 200
    
    except (Exception, Error) as error:
        print("Error connecting to the database:", error)
        return jsonify({'error': str(error)})

    finally:
        cur.close()
        conn.close()
        

@app.route('/position_rssi', methods=['POST']) # send data
def insert_rssi():
    try:
        conn = connect_db_Anchor()
        cur = conn.cursor()

        # Get the name and rssi from the request parameters
        data = request.get_json()

        x = str(data.get('x'))  
        y = str(data.get('y'))  
        error = str(data.get('error')) 
        status = data.get('status')
        
        cur.execute("SELECT id FROM rssi_data ORDER BY id DESC LIMIT 1")
        rssi_id = cur.fetchone()[0]  # ดึงค่าเดียวออกมา
        
        cur.execute("INSERT INTO position_rssi(rssi_data_id, x, y, error_distance, status, timestamp) VALUES (%s, %s, %s, %s, %s, to_timestamp(to_char(now(), 'YYYY-MM-DD HH24:MI:SS'), 'YYYY-MM-DD HH24:MI:SS'))", (rssi_id, x, y, error, status,))
        conn.commit()

        return jsonify({"message": "Data inserted successfully."}), 200
    
    except (Exception, Error) as error:
        print("Error connecting to the database:", error)
        return jsonify({'error': str(error)})

    finally:
        cur.close()
        conn.close()
        
        
@app.route('/Point', methods=['GET'])
def get_point():
    try:        
        conn = connect_db_Anchor()
        cur = conn.cursor()

        data = request.get_json()
        if not data or "point" not in data:
            return jsonify({"error": "Missing 'point' parameter"}), 400

        point = data["point"]
        if point not in ["A", "B", "C", "D", "E", "F"]:
            return jsonify({"error": "Invalid point value. Must be 'A', 'B', 'C', 'D', 'E' or 'F'"}), 400

        cur.execute("SELECT x, y FROM point WHERE point_id = %s", (point,))
        result = cur.fetchone()

        if result:
            x, y = result
            return jsonify({"point": point, "x": float(x), "y": float(y)}), 200
        else:
            return jsonify({"error": "No data found for the given point"}), 404
    
    except (Exception, Error) as error:
        print("Error connecting to the database:", error)
        return jsonify({'error': str(error)})

    finally:
        cur.close()
        conn.close()
        
        
@app.route('/Point_Map_aoa', methods=['GET'])
def get_point_map_aoa():
    try:        
        conn = connect_db_Anchor()
        cur = conn.cursor()

        data = request.get_json()
        point = data.get("point")
        if not data or "point" not in data:
            return jsonify({"error": "Missing 'point' parameter"}), 400

        point = data["point"]
        if point not in ["A", "B", "C", "D", "E", "F"]:
            return jsonify({"error": "Invalid point value. Must be 'A', 'B', 'C', 'D', 'E' or 'F'"}), 400

        # คำสั่ง SQL ดึงข้อมูล x, y ที่มี point ตรงกัน
        query = """
            SELECT pa.x, pa.y
            FROM position_aoa pa
            JOIN rssi_data rd ON pa.rssi_data_id = rd.id
            WHERE rd.point_id = %s;
        """
        cur.execute(query, (point,))
        result = cur.fetchall()  # ดึงข้อมูลทั้งหมด

        # แปลงข้อมูลเป็น JSON
        points_list = [{"x": row[0], "y": row[1]} for row in result]

        return jsonify(points_list)  # ส่งกลับค่า x, y ทั้งหมดในรูปแบบ JSON
    
    except (Exception, Error) as error:
        print("Error connecting to the database:", error)
        return jsonify({'error': str(error)})

    finally:
        cur.close()
        conn.close()
        
        
@app.route('/Point_Map_rssi', methods=['GET'])
def get_point_map_rssi():
    try:        
        conn = connect_db_Anchor()
        cur = conn.cursor()

        data = request.get_json()
        point = data.get("point")
        if not data or "point" not in data:
            return jsonify({"error": "Missing 'point' parameter"}), 400

        point = data["point"]
        if point not in ["A", "B", "C", "D", "E", "F"]:
            return jsonify({"error": "Invalid point value. Must be 'A', 'B', 'C', 'D', 'E' or 'F'"}), 400

        # คำสั่ง SQL ดึงข้อมูล x, y ที่มี point ตรงกัน
        query = """
            SELECT pr.x, pr.y
            FROM position_rssi pr
            JOIN rssi_data rd ON pr.rssi_data_id = rd.id
            WHERE rd.point_id = %s;
        """
        cur.execute(query, (point,))
        result = cur.fetchall()  # ดึงข้อมูลทั้งหมด

        # แปลงข้อมูลเป็น JSON
        points_list = [{"x": row[0], "y": row[1]} for row in result]

        return jsonify(points_list)  # ส่งกลับค่า x, y ทั้งหมดในรูปแบบ JSON
    
    except (Exception, Error) as error:
        print("Error connecting to the database:", error)
        return jsonify({'error': str(error)})

    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)