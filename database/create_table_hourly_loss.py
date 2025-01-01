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
    # Create hourly loss table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hourly_loss (
        max_person INTEGER,
        count_sub_project INTEGER,
        total_cost INTEGER,
        loss_calculation INTEGER,
        calculate_time TIMESTAMP
    );
    """)
    
    # Add project_id column in sub project table
    cursor.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='hourly_loss' AND column_name='project_id') THEN
            ALTER TABLE hourly_loss ADD COLUMN project_id INTEGER;
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
            AND table_name = 'hourly_loss'
            AND constraint_name = 'fk_project'
        ) THEN
            ALTER TABLE hourly_loss
            ADD CONSTRAINT fk_project
            FOREIGN KEY (project_id) REFERENCES project(id);
        END IF;
    END
    $$;
    """)

    conn.commit() 
    print("Tables created successfully.")

except psycopg2.Error as e:
    print(f"Database error: {e}")

finally:
    # Close database connection
    cursor.close()
    conn.close()
