import psycopg2  # type: ignore

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
        video_path VARCHAR,
        cctv_id INTEGER,
        job_id INTEGER
    );
    """)
    
    # Create loss_analysis table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loss_analysis (
        id SERIAL PRIMARY KEY,
        detection_count INTEGER,
        timesheet_count INTEGER,
        hour_intime INTEGER,
        hour_overtime INTEGER,
        hour_loss INTEGER,
        hour_overtime_calc FLOAT,
        hour_loss_calc FLOAT,
        expected_progress FLOAT,
        total_progress FLOAT,
        calculate_time TIMESTAMP,
        cctv_id INTEGER
    );
    """)

    # Create cctv table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cctv (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        rtsp_url VARCHAR(255),
        work_center_id INTEGER
    );
    """)

    # Create job table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job (
        id SERIAL PRIMARY KEY,
        job_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Add constraints for foreign keys
    cursor.execute("""
    ALTER TABLE person_count_max
    ADD CONSTRAINT fk_cctv
    FOREIGN KEY (cctv_id) REFERENCES cctv(id);
    """)
    
    cursor.execute("""
    ALTER TABLE person_count_max
    ADD CONSTRAINT fk_job
    FOREIGN KEY (job_id) REFERENCES job(id);
    """)
    
    cursor.execute("""
    ALTER TABLE cctv
    ADD CONSTRAINT fk_work_center
    FOREIGN KEY (work_center_id) REFERENCES work_center(id);
    """)
    
    cursor.execute("""
    ALTER TABLE loss_analysis
    ADD CONSTRAINT fk_cctv_loss_analysis
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
