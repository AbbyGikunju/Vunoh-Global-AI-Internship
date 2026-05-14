import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():

    conn = psycopg2.connect(DATABASE_URL) 
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    with open('schema.sql', 'r') as f:
        cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()        