import requests
import psycopg2
from config import API_ENDPOINT, API_KEY, BASE_CURRENCY, HOST, PORT, DB_NAME, USER, PASSWORD

host = HOST
port = PORT
db_name = DB_NAME
user = USER
password = PASSWORD

# Establishing connection with the database
connection = psycopg2.connect(
    host = host,
    port= port,
    dbname = db_name,
    user = user,
    password = password
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
target_currency = "GBP"
amount = 5

headers = {
    "apikey": API_KEY
}

# Make API request
response = requests.get(url, headers=headers, params={
    "to": target_currency,
    "from": BASE_CURRENCY,
    "amount": amount
})

# Processing the API response
status_code = response.status_code
result = response.json()

exchange_rate = result.get("result")

# Storing the exchange rate in the database
insert_query = """
    INSERT INTO exchange_rates (base_currency, target_currency, rate)
    VALUES (%s, %s, %s)
"""
data = (BASE_CURRENCY, target_currency, exchange_rate)
cursor.execute(insert_query, data)

connection.commit()

cursor.close()
connection.close()



