from copy import error
import psycopg2

def get_products():
    products_list = []
    try:
        #connect to PostgresSQL
        connection = psycopg2.connect(
            host="localhost",
            database="postgres",
            user="postgres",
            password="DanFay29$1"
        )

        cursor = connection.cursor()

        #Query to get products
        cursor.execute("SELECT name, unit_price FROM postgres.danfay.products")
        products = cursor.fetchall()
        for prd in products:
           products_list.append({"name": prd[0], "unit_price": prd[1]})

    except psycopg2.Error as db_error:
        print(f"Database Error: {db_error}")
        products_list = []

    except Exception as error:
        print(f"General Exception Error:{error}")

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    print(f"name:{products_list[0]['name']}")
    return products_list

if __name__ == "__main__":
    print(get_products())