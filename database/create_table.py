import psycopg2 # type: ignore

# Create connection
conn = psycopg2.connect(
    dbname='human_detection',
    user='postgres',
    password='admin@123',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()

try:
    # Create person count raw table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS person_counts (
        frame INTEGER,
        timestamp VARCHAR,
        person_count INTEGER,
        UNIQUE (frame, timestamp)
    );
    """)

    # Create person count max table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS person_count_max (
        max_value INTEGER,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        video_path VARCHAR
    );
    """)

    # Create cctv table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cctv (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        location VARCHAR(255),
        rtsp_url VARCHAR(255)
    );
    """)
    
    # Create failed job table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job (
        id SERIAL PRIMARY KEY,
        job_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)    

    # Add cctv_id column in person count max table
    cursor.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='person_count_max' AND column_name='cctv_id') THEN
            ALTER TABLE person_count_max ADD COLUMN cctv_id INTEGER;
        END IF;
    END
    $$;
    """)

    # Add constrain cctv_id
    cursor.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.table_constraints
            WHERE constraint_type = 'FOREIGN KEY'
            AND table_name = 'person_count_max'
            AND constraint_name = 'fk_cctv'
        ) THEN
            ALTER TABLE person_count_max
            ADD CONSTRAINT fk_cctv
            FOREIGN KEY (cctv_id) REFERENCES cctv(id);
        END IF;
    END
    $$;
    """)
    
    # Add job_id column in person count max table
    cursor.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='person_count_max' AND column_name='job_id') THEN
            ALTER TABLE person_count_max ADD COLUMN job_id INTEGER;
        END IF;
    END
    $$;
    """)
    
    # Add constrain job_id
    cursor.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.table_constraints
            WHERE constraint_type = 'FOREIGN KEY'
            AND table_name = 'person_count_max'
            AND constraint_name = 'fk_job'
        ) THEN
            ALTER TABLE person_count_max
            ADD CONSTRAINT fk_job
            FOREIGN KEY (job_id) REFERENCES job(id);
        END IF;
    END
    $$;
    """)

    conn.commit() 
    print("Tables and constraints created successfully.")

except psycopg2.Error as e:
    print(f"Database error: {e}")

finally:
    # Close database connection
    cursor.close()
    conn.close()
