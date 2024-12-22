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
    # Create main project table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project (
        id SERIAL PRIMARY KEY,
        nama_ketua VARCHAR,
        nama_projek VARCHAR,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        total_cost INTEGER
    );
    """)

    # Create sub project table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sub_project (
        nama_pekerja VARCHAR,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        cost INTEGER
    );
    """)

    # Add project_id column in sub project table
    cursor.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='sub_project' AND column_name='project_id') THEN
            ALTER TABLE sub_project ADD COLUMN project_id INTEGER;
        END IF;
    END
    $$;
    """)

    # Add constrain project_id
    cursor.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.table_constraints
            WHERE constraint_type = 'FOREIGN KEY'
            AND table_name = 'sub_project'
            AND constraint_name = 'fk_project'
        ) THEN
            ALTER TABLE sub_project
            ADD CONSTRAINT fk_project
            FOREIGN KEY (project_id) REFERENCES project(id);
        END IF;
    END
    $$;
    """)
    
    # Add cctv_id column in project table
    cursor.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='project' AND column_name='cctv_id') THEN
            ALTER TABLE project ADD COLUMN cctv_id INTEGER;
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
            AND table_name = 'project'
            AND constraint_name = 'fk_cctv_project'
        ) THEN
            ALTER TABLE project
            ADD CONSTRAINT fk_cctv_project
            FOREIGN KEY (cctv_id) REFERENCES cctv(id);
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
