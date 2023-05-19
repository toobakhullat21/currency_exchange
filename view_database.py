import psycopg2

from config import HOST, PORT, DB_NAME, USER, PASSWORD

def view_exchange_rates():
    # Establishing connection with the database
    connection = psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DB_NAME,
        user=USER,
        password=PASSWORD
    )

    cursor = connection.cursor()

    # Execute the select query to fetch exchange rates from the database
    select_query = "SELECT * FROM exchange_rates"
    cursor.execute(select_query)
    exchange_rates = cursor.fetchall()

    for rate in exchange_rates:
        print(rate)

    cursor.close()
    connection.close()

view_exchange_rates()