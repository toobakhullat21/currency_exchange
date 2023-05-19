import json
import requests
import redis
import psycopg2
from config import API_ENDPOINT, HOST, PORT, DB_NAME, USER, PASSWORD, REDIS_HOST, REDIS_PORT, REDIS_DB

def convert_currency(base_currency, target_currency, amount):
    # Establishing connection with the database
    connection = psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DB_NAME,
        user=USER,
        password=PASSWORD
    )

    cursor = connection.cursor()

    # if "exchange_rates" table does not exist, create one
    create_table_query = """
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id SERIAL PRIMARY KEY,
            base_currency VARCHAR(3),
            target_currency VARCHAR(3),
            rate NUMERIC
        )
    """
    cursor.execute(create_table_query)

    connection.commit()

    url = API_ENDPOINT

    # Creating a Redis cache connection
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

    # Check if the exchange rate is already cached in Redis
    cache_key = f"exchange_rate:{base_currency}:{target_currency}"
    cached_rate = redis_client.get(cache_key)

    if cached_rate:
        exchange_rate = float(cached_rate.decode())
    else:
        # Fetch the exchange rate from the API
        response = requests.get(url, params={
            "base": base_currency,
            "symbols": target_currency
        })
        result = response.json()

        if "error" in result:
            print(f"Error retrieving exchange rate: {result['error']}")
            exchange_rate = None
        else:
            exchange_rate = result["rates"].get(target_currency)

            # Store the exchange rate in Redis cache
            if exchange_rate is not None:
                redis_client.set(cache_key, exchange_rate)
                redis_client.expire(cache_key, 3600)  # Set cache expiry time to 1 hour

    # Only proceed if the exchange rate is not None
    if exchange_rate is not None:
        converted_amount = amount * exchange_rate
        # print(f"{amount} {base_currency} = {converted_amount} {target_currency}")

        # Storing the exchange rate in the database
        insert_query = """
            INSERT INTO exchange_rates (base_currency, target_currency, rate)
            VALUES (%s, %s, %s)
        """
        data = (base_currency, target_currency, exchange_rate)
        cursor.execute(insert_query, data)

    connection.commit()

    cursor.close()
    connection.close()



