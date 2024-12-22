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
        ('Beni', 'Projek A', datetime(2024, 1, 1, 0, 0), datetime(2024, 1, 30, 23, 0), 50000000, 1),
        ('Akil', 'Projek B', datetime(2024, 2, 1, 0, 0), datetime(2024, 2, 28, 23, 0), 7500000, 2),
    ]

    # Insert Query
    insert_project_query = """
    INSERT INTO project (nama_ketua, nama_projek, start_time, end_time, total_cost, cctv_id)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    cursor.executemany(insert_project_query, project_data)
    
    # Create data sub project
    sub_project_data = [
        ('Hela', datetime(2024, 12, 10, 7, 0), datetime(2024, 12, 10, 17, 0), 750000, 1),
        ('Doni', datetime(2024, 12, 10, 13, 0), datetime(2024, 12, 10, 17, 0), 250000, 1),
        ('Jajang', datetime(2024, 12, 10, 9, 0), datetime(2024, 12, 10, 17, 0), 300000, 1),
        ('Deni', datetime(2024, 12, 10, 7, 0), datetime(2024, 12, 10, 17, 0), 750000, 1),
        ('Elok', datetime(2024, 12, 10, 13, 0), datetime(2024, 12, 10, 17, 0), 250000, 1),
        ('Ulyo', datetime(2024, 12, 10, 9, 0), datetime(2024, 12, 10, 17, 0), 300000, 1),
        ('Beril', datetime(2024, 12, 10, 7, 0), datetime(2024, 12, 10, 17, 0), 750000, 1),
        ('Ucup', datetime(2024, 12, 10, 13, 0), datetime(2024, 12, 10, 17, 0), 250000, 1),
        ('Galih', datetime(2024, 12, 10, 9, 0), datetime(2024, 12, 10, 17, 0), 300000, 1),
        ('Heri', datetime(2024, 12, 10, 7, 0), datetime(2024, 12, 10, 17, 0), 750000, 1),
        ('Sofyan', datetime(2024, 12, 10, 13, 0), datetime(2024, 12, 10, 17, 0), 250000, 1),
        ('Budi', datetime(2024, 12, 10, 9, 0), datetime(2024, 12, 10, 17, 0), 300000, 1),
        ('Garry', datetime(2024, 12, 10, 7, 0), datetime(2024, 12, 10, 17, 0), 750000, 1),
        ('Dedy', datetime(2024, 12, 10, 13, 0), datetime(2024, 12, 10, 17, 0), 250000, 1),
        ('Hotman', datetime(2024, 12, 10, 9, 0), datetime(2024, 12, 10, 17, 0), 300000, 1),
        ('Priyo', datetime(2024, 12, 10, 7, 0), datetime(2024, 12, 10, 17, 0), 750000, 1),
        ('Gogon', datetime(2024, 12, 10, 13, 0), datetime(2024, 12, 10, 17, 0), 250000, 1),
        ('Gafin', datetime(2024, 12, 10, 9, 0), datetime(2024, 12, 10, 17, 0), 300000, 1),
        ('Yori', datetime(2024, 12, 10, 7, 0), datetime(2024, 12, 10, 17, 0), 750000, 1),
        ('Bong', datetime(2024, 12, 10, 13, 0), datetime(2024, 12, 10, 17, 0), 250000, 1),
    ]
    
    # Insert Query
    insert_sub_project_query = """
    INSERT INTO sub_project (nama_pekerja, start_time, end_time, cost, project_id)
    VALUES (%s, %s, %s, %s, %s);
    """
    cursor.executemany(insert_sub_project_query, sub_project_data)

    conn.commit()
    print("Data seeded successfully.")

except psycopg2.Error as e:
    print(f"Database error: {e}")

finally:
    # Close database connection
    cursor.close()
    conn.close()
