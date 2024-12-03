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
    # Create main project table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project (
        id SERIAL PRIMARY KEY,
        leader_name VARCHAR,
        project_name VARCHAR,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        total_cost INTEGER,
        plan_hour INTEGER,
        progress FLOAT
    );
    """)
    
    # Create work center table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS work_center (
        id SERIAL PRIMARY KEY,
        workshop_name VARCHAR,
        project_id INTEGER
    );
    """)
    
    # Create employee table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee (
        id SERIAL PRIMARY KEY,
        employee_name VARCHAR,
        work_center_id INTEGER
    );
    """)
    
    # Create time sheet table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS time_sheet (
        id SERIAL PRIMARY KEY,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        cost_per_hour INTEGER,
        cost_total INTEGER,
        work_center_id INTEGER,
        employee_id INTEGER
    );
    """)

    # Add constraints for foreign keys
    cursor.execute("""
    ALTER TABLE work_center
    ADD CONSTRAINT fk_project
    FOREIGN KEY (project_id) REFERENCES project(id);
    """)

    cursor.execute("""
    ALTER TABLE employee
    ADD CONSTRAINT fk_work_center_employee
    FOREIGN KEY (work_center_id) REFERENCES work_center(id);
    """)

    cursor.execute("""
    ALTER TABLE time_sheet
    ADD CONSTRAINT fk_work_center_timesheet
    FOREIGN KEY (work_center_id) REFERENCES work_center(id);
    """)
    
    cursor.execute("""
    ALTER TABLE time_sheet
    ADD CONSTRAINT fk_employee_timesheet
    FOREIGN KEY (employee_id) REFERENCES employee(id);
    """)

    conn.commit() 
    print("Tables and constraints created successfully.")

except psycopg2.Error as e:
    print(f"Database error: {e}")

finally:
    # Close database connection
    cursor.close()
    conn.close()
