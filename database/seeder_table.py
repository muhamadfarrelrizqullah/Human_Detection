import psycopg2 # type: ignore
from datetime import datetime

# Create connection
conn = psycopg2.connect(
    dbname='worker_detection',
    user='postgres',
    password='admin@123',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()

try:
    # Create data cctv
    cctv_data = [
        ('CCTV 1', 'rtsp://username:password@ip_address:port/stream1', 'Bengkel X'),
        ('CCTV 2', 'rtsp://username:password@ip_address:port/stream2', 'Bengkel Y'),
    ]
    # Insert Query
    insert_query = """
    INSERT INTO cctv (name, rtsp_url, location) 
    VALUES (%s, %s, %s);
    """
    cursor.executemany(insert_query, cctv_data)

    conn.commit()
    print("Data seeded successfully.")

except psycopg2.Error as e:
    print(f"Database error: {e}")

finally:
    # Close database connection
    cursor.close()
    conn.close()
