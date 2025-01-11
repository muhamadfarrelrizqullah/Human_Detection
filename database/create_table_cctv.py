import psycopg2  # type: ignore

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
    # Create person_counts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS person_counts (
        frame INTEGER,
        timestamp VARCHAR,
        person_count INTEGER,
        UNIQUE (frame, timestamp)
    );
    """)

    # Create person_count_max table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS person_count_max (
        id SERIAL PRIMARY KEY,
        max_value INTEGER,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        cctv_id INTEGER
    );
    """)
    
    # Create cctv table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cctv (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        rtsp_url VARCHAR(255),
        location VARCHAR(255)
    );
    """)

    # Add constraints for foreign keys
    cursor.execute("""
    ALTER TABLE person_count_max
    ADD CONSTRAINT fk_cctv
    FOREIGN KEY (cctv_id) REFERENCES cctv(id);
    """)

    conn.commit()
    print("Tables and constraints created successfully.")

except psycopg2.Error as e:
    print(f"Database error: {e}")

finally:
    # Close database connection
    cursor.close()
    conn.close()
