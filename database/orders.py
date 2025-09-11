
from .db_session import create_session
import psycopg2
from datetime import date, datetime
from decimal import Decimal

def get_orders():
    orders_list = []
    try:
        connection = create_session()
        cursor = connection.cursor()

        #Query to get orders
        cursor.execute("SELECT * FROM danfay.public.orders")
        orders = cursor.fetchall()
        if not orders:
            print("No orders found.")
            return []
        
        for ord in orders:
           orders_list.append({"orderno": ord[0], "orderdate": ord[1]})

    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")
        orders_list = []

    except Exception as error:
        print(f"General Exception Error:{error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    print(f"order No:{orders_list[0]['orderno']}")
    return orders_list

def insert_order(orderNo: str, orderDate: datetime, qty: int, platform: str, orderAmount: Decimal, salesTax: Decimal, itemCost:Decimal, comments: str, status:str ) -> bool:
    try:
        connection = create_session()
        cursor = connection.cursor()

        # Insert order
        cursor.execute(
            "INSERT INTO danfay.public.orders (orderno, orderdate, qty, platform, orderamount, salestax, itemcost, comments, status )" 
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
            (orderNo, orderDate, qty, platform, orderAmount, salesTax, itemCost, comments, status)
        )
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

if __name__ == "__main__":
   print(get_orders())

#    insert_order("123456", date.fromisoformat("2025-09-10"), 1, "Etsy", 59.95, 2.25, 20.16, "add test", "completed")

