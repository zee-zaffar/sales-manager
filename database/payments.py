import psycopg2
from psycopg2 import sql
from .db_session import create_session
# --- Payments CRUD ---
def add_payment(shipmentheaderid, paymentdate, description, amount, fee, comments=None):
    try:
        connection = create_session()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO payments (shipmentheaderid, paymentdate, description, amount, fee, comments)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING ID;
        """, (shipmentheaderid, paymentdate, description, amount, fee, comments))
        payment_id = cursor.fetchone()[0]
        connection.commit()
        return payment_id
    
    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")

    except Exception as error:
        print(f"General Exception Error:{error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def update_payment(id, shipmentheaderid, paymentdate, description, amount, fee, comments=None):
    try:
        connection = create_session()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE payments SET shipmentheaderid=%s, paymentdate=%s, description=%s, amount=%s, fee=%s, comments=%s
            WHERE id=%s;
        """, (shipmentheaderid, paymentdate, description, amount, fee, comments, id))
        connection.commit()

    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")

    except Exception as error:
        print(f"General Exception Error:{error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def delete_payment(id):
    try:
        connection = create_session()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM payments WHERE id=%s;", (id,))
        connection.commit()
    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")

    except Exception as error:
        print(f"General Exception Error:{error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_payment(id):
    try:
        connection = create_session()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM payments WHERE id=%s;", (id,))
        payment = cursor.fetchone()
        return payment
    
    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")

    except Exception as error:
        print(f"General Exception Error:{error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_payments_by_shipmentheader(shipmentheaderid):
    try:
        connection = create_session()
        cursor = connection.cursor()
        cursor.execute("SELECT id, shipmentheaderid, paymentdate, description,amount,fee, comments FROM Payments WHERE shipmentheaderid=%s", (shipmentheaderid,))
        payments = [
            {
                'ID': r[0],
                'ShipmentHeaderId': r[1],
                'PaymentDate': r[2],
                'Description': r[3],
                'Amount': r[4],
                'Fee': r[5],
                'Comments': r[6]
            }
            for r in cursor.fetchall()
        ]
        return payments
    
    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")

    except Exception as error:
        print(f"General Exception Error:{error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
