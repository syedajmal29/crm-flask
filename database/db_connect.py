import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="crm_db",
        user="your_db_user",
        password="your_db_password"
    )
