import psycopg2 # type: ignore

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname='human_detection',
    user='postgres',
    password='admin@123',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()

# Truncate the table
cursor.execute("TRUNCATE TABLE person_counts;")
conn.commit()

# Close database connection
cursor.close()
conn.close()
