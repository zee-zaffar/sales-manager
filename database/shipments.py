import psycopg2
from psycopg2 import sql
from .db_session import create_session

# --- ShipmentHeader CRUD ---
def get_shipment(id):
    try:
        connection = create_session()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM shipments WHERE id=%s;", (id,))
        shipment = cursor.fetchone()
        return shipment
    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")

    except Exception as error:
        print(f"General Exception Error:{error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_shipment_header(shipment_id):
    connection = create_session()
    cur = connection.cursor()
    cur.execute("SELECT ID, SupplierName, ShipmentNo, DateReceived, Comments FROM ShipmentHeader WHERE ID=%s", (shipment_id,))
    row = cur.fetchone()
    cur.close()
    connection.close()
    if row:
        return {
            'ID': row[0],
            'SupplierName': row[1],
            'ShipmentNo': row[2],
            'DateReceived': row[3],
            'Comments': row[4]
        }
    return None

def get_shipment_details(shipment_id):
    connection = create_session()
    cur = connection.cursor()
    cur.execute("SELECT ID, Description, SKU, Quantity, UnitPrice, Comments FROM ShipmentDetail WHERE ShipmentHeaderID=%s", (shipment_id,))
    details = [
        {
            'ID': r[0],
            'Description': r[1],
            'SKU': r[2],
            'Quantity': r[3],
            'UnitPrice': r[4],
            'Comments': r[5]
        }
        for r in cur.fetchall()
    ]
    cur.close()
    connection.close()
    return details

def get_shipments():
    try:
        connection = create_session()
        cursor = connection.cursor()
     
        cursor.execute("SELECT ID, SupplierName, ShipmentNo, DateReceived, Comments FROM ShipmentHeader ORDER BY DateReceived DESC;")
        shipments = [
            {
                'ID': row[0],
                'SupplierName': row[1],
                'ShipmentNo': row[2],
                'DateReceived': row[3],
                'Comments': row[4]
            }
            for row in cursor.fetchall()
        ]
        print(f"Total shipments found: {len(shipments)}")
        return shipments
    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")

    except Exception as error:
        print(f"General Exception Error:{error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            
def add_shipment_header(supplier_name, shipment_no, date_received, comments=None)-> int:

    try:
        connection = create_session()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO ShipmentHeader (SupplierName, ShipmentNo, DateReceived, Comments)
            VALUES (%s, %s, %s, %s) RETURNING ID;
        """, (supplier_name, shipment_no, date_received, comments))

        shipment_id = cursor.fetchone()[0]
        connection.commit()
        return shipment_id
    
    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")

    except Exception as error:
        print(f"General Exception Error:{error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def update_shipment_header(id, supplier_name, shipment_no, date_received, comments=None)-> bool:
    try:
        connection = create_session()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE ShipmentHeader SET SupplierName=%s, ShipmentNo=%s, DateReceived=%s, Comments=%s
            WHERE ID=%s;
        """, (supplier_name, shipment_no, date_received, comments, id))
        connection.commit()
        return True
      
    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")
        return False

    except Exception as error:
        print(f"General Exception Error:{error}")
        return False

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def delete_shipment_header(id)-> bool:
    try:
        connection = create_session()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM ShipmentHeader WHERE ID=%s;", (id,))
        connection.commit()
        return True
    
    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")
        return False

    except Exception as error:
        print(f"General Exception Error:{error}")
        return False

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# --- ShipmentDetail CRUD ---
def add_shipment_detail(header_id, description, sku, quantity, unit_price, comments=None)-> int:
    try:
            connection = create_session()
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO ShipmentDetail (ShipmentHeaderID, Description, SKU, Quantity, UnitPrice, Comments)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING ID;
            """, (header_id, description, sku, quantity, unit_price, comments))
            detail_id = cursor.fetchone()[0]
            connection.commit()
            return detail_id
    
    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")
        return False

    except Exception as error:
        print(f"General Exception Error:{error}")
        return False

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def update_shipment_detail(id, header_id, description, sku, quantity, unit_price, comments=None):
    try:
        connection = create_session()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE ShipmentDetail SET ShipmentHeaderID=%s, Description=%s, SKU=%s, Quantity=%s, UnitPrice=%s, Comments=%s
            WHERE ID=%s;
        """, (header_id, description, sku, quantity, unit_price, comments, id))
        connection.commit()

    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")
        return False

    except Exception as error:
        print(f"General Exception Error:{error}")
        return False

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def delete_shipment_detail(id)-> bool:
    try:
        connection = create_session()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM ShipmentDetail WHERE ID=%s;", (id,))
        connection.commit()
        return
    
    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")
        return False

    except Exception as error:
        print(f"General Exception Error:{error}")
        return False

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
