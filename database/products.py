
from .db_session import create_session
import psycopg2

def get_products():
    products_list = []
    try:
        connection = create_session()
        cursor = connection.cursor()

        #Query to get products
        cursor.execute("SELECT * FROM danfay.public.products")
        products = cursor.fetchall()
        for prd in products:
           products_list.append({"code": prd[0], "category": prd[1]})

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

    print(f"code:{products_list[0]['code']}")
    return products_list

def insert_product(code: str, category: str, desc: str, color: str, ) -> bool:
    try:
        connection = create_session()
        cursor = connection.cursor()

        # Insert product
        cursor.execute(
            "INSERT INTO danfay.public.products (productcode, productcategory, productdesc, color, productcost)" 
            "VALUES (%s, %s, %s, %s, 0.0);",
            (code, category, desc, color, )
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
   print(get_products())

   # insert_product("P1002", "Category1", "Description1", "Red")

