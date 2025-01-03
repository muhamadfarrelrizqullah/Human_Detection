import psycopg2 # type: ignore
from datetime import datetime

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
    # Create data project
    project_data = [
        ('Beni', 'Projek A', datetime(2024, 1, 1, 0, 0), datetime(2024, 1, 30, 23, 0), 50000000, 100, 30),
        ('Akil', 'Projek B', datetime(2024, 2, 1, 0, 0), datetime(2024, 2, 28, 23, 0), 800000, 80, 10),
    ]
    # Insert Query
    insert_query_project = """
    INSERT INTO project (leader_name, project_name, start_time, end_time, total_cost, plan_hour, progress) 
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    cursor.executemany(insert_query_project, project_data)
    
    # Create data work_center
    work_center_data = [
        ('Bengkel A', 1),
        ('Bengkel B', 2),
    ]
    # Insert Query
    insert_query_work_center = """
    INSERT INTO work_center (workshop_name, project_id) 
    VALUES (%s, %s);
    """
    cursor.executemany(insert_query_work_center, work_center_data)
    
    # Create data cctv
    cctv_data = [
        ('CCTV 1', 'rtsp://username:password@ip_address:port/stream1', 1),
        ('CCTV 2', 'rtsp://username:password@ip_address:port/stream2', 2),
    ]
    # Insert Query
    insert_query = """
    INSERT INTO cctv (name, rtsp_url, work_center_id) 
    VALUES (%s, %s, %s);
    """
    cursor.executemany(insert_query, cctv_data)
    
    # Create data employee
    employee_data = [
        ('Hela', 1),
        ('Doni', 1),
        ('Jajang', 1),
        ('Deni', 1),
        ('Elok', 1),
        ('Ulyo', 1),
        ('Beril', 1),
        ('Ucup', 1),
        ('Galih', 1),
        ('Heri', 1),
        ('Sofyan', 1),
        ('Budi', 1),
        ('Garry', 1),
        ('Dedy', 1),
        ('Hotman', 1),
        ('Priyo', 1),
        ('Gogon', 1),
        ('Gafin', 1),
        ('Yori', 1),
        ('Bong', 1),
    ]
    # Insert Query
    insert_query_employee = """
    INSERT INTO employee (employee_name, work_center_id) 
    VALUES (%s, %s);
    """
    cursor.executemany(insert_query_employee, employee_data)
    
    # Create data time_sheet
    time_sheet_data = [
        (datetime(2024, 12, 10, 7, 0), datetime(2024, 12, 10, 17, 0), 80000, 640000, 1, 1),
        (datetime(2024, 12, 10, 13, 0), datetime(2024, 12, 10, 17, 0), 25000, 200000, 1, 2),
        (datetime(2024, 12, 10, 9, 0), datetime(2024, 12, 10, 17, 0), 30000, 240000, 1, 3),
        (datetime(2024, 12, 10, 7, 0), datetime(2024, 12, 10, 17, 0), 80000, 640000, 1, 4),
        (datetime(2024, 12, 10, 13, 0), datetime(2024, 12, 10, 17, 0), 25000, 200000, 1, 5),
        (datetime(2024, 12, 10, 9, 0), datetime(2024, 12, 10, 17, 0), 30000, 240000, 1, 6),
        (datetime(2024, 12, 10, 7, 0), datetime(2024, 12, 10, 17, 0), 80000, 640000, 1, 7),
        (datetime(2024, 12, 10, 13, 0), datetime(2024, 12, 10, 17, 0), 25000, 200000, 1, 8),
        (datetime(2024, 12, 10, 9, 0), datetime(2024, 12, 10, 17, 0), 30000, 240000, 1, 9),
        (datetime(2024, 12, 10, 7, 0), datetime(2024, 12, 10, 17, 0), 80000, 640000, 1, 10),
        (datetime(2024, 12, 10, 13, 0), datetime(2024, 12, 10, 17, 0), 25000, 200000, 1, 11),
        (datetime(2024, 12, 10, 9, 0), datetime(2024, 12, 10, 17, 0), 30000, 240000, 1, 12),
        (datetime(2024, 12, 10, 7, 0), datetime(2024, 12, 10, 17, 0), 80000, 640000, 1, 13),
        (datetime(2024, 12, 10, 13, 0), datetime(2024, 12, 10, 17, 0), 25000, 200000, 1, 14),
        (datetime(2024, 12, 10, 9, 0), datetime(2024, 12, 10, 17, 0), 30000, 240000, 1, 15),
        (datetime(2024, 12, 10, 7, 0), datetime(2024, 12, 10, 17, 0), 80000, 640000, 1, 16),
        (datetime(2024, 12, 10, 13, 0), datetime(2024, 12, 10, 17, 0), 25000, 200000, 1, 17),
        (datetime(2024, 12, 10, 9, 0), datetime(2024, 12, 10, 17, 0), 30000, 240000, 1, 18),
        (datetime(2024, 12, 10, 7, 0), datetime(2024, 12, 10, 17, 0), 80000, 640000, 1, 19),
        (datetime(2024, 12, 10, 13, 0), datetime(2024, 12, 10, 17, 0), 25000, 200000, 1, 20),
    ]
    # Insert Query
    insert_query_time_sheet = """
    INSERT INTO time_sheet (start_time, end_time, cost_per_hour, cost_total, work_center_id, employee_id ) 
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    cursor.executemany(insert_query_time_sheet, time_sheet_data)

    conn.commit()
    print("Data seeded successfully.")

except psycopg2.Error as e:
    print(f"Database error: {e}")

finally:
    # Close database connection
    cursor.close()
    conn.close()
