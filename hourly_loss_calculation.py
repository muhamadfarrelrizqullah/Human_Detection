import psycopg2  # type: ignore
from datetime import datetime, timedelta

# Create database connection
conn = psycopg2.connect(
    dbname='human_detection',
    user='postgres',
    password='admin@123',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()

try:
    # Get today's date range
    today = datetime(2024, 12, 10)
    start_of_hour = today.replace(hour=10, minute=0, second=0, microsecond=0)
    end_of_hour = start_of_hour + timedelta(hours=1)

    if start_of_hour is not None:
        # Query to fetch the maximum `max_person_count` within the hour range
        cursor.execute(
            """
            SELECT MAX(max_value) AS max_person_count
            FROM person_count_max
            WHERE start_time >= %s AND end_time < %s;
            """,
            (start_of_hour, end_of_hour)
        )
        # Fetch and display the result
        result = cursor.fetchone()
        max_person_count = result[0] if result else None
        if max_person_count is not None:
            print(f"Maximum person count for ({start_of_hour.strftime('%Y-%m-%d %H:%M:%S')}) to ({end_of_hour.strftime('%Y-%m-%d %H:%M:%S')}): {max_person_count}")
        else:
            max_person_count = 0
            print(f"No data available for the time range ({start_of_hour.strftime('%Y-%m-%d %H:%M:%S')}) to ({end_of_hour.strftime('%Y-%m-%d %H:%M:%S')}).")

        # Query to fetch the count of sub_projects within the same hour range
        cursor.execute(
            """
            SELECT COUNT(*) 
            FROM sub_project 
            WHERE (start_time >= %s AND start_time < %s)
            OR (end_time > %s AND end_time <= %s)
            OR (start_time <= %s AND end_time >= %s);
            """,
            (start_of_hour, end_of_hour, start_of_hour, end_of_hour, start_of_hour, end_of_hour)
        )
        # Fetch and display the result for sub-project count
        result_worksheet = cursor.fetchone()
        count_sub_project = result_worksheet[0] if result_worksheet else None
        if count_sub_project is not None:
            print(f"Sub-project count for ({start_of_hour.strftime('%Y-%m-%d %H:%M:%S')}) to ({end_of_hour.strftime('%Y-%m-%d %H:%M:%S')}): {count_sub_project}")
        else:
            count_sub_project = 0
            print(f"No sub-project data available for the time range ({start_of_hour.strftime('%Y-%m-%d %H:%M:%S')}) to ({end_of_hour.strftime('%Y-%m-%d %H:%M:%S')}).")

        # Hourly loss calculation
        if max_person_count < count_sub_project:
            # Query to calculate total cost per hour for the sub-projects working in the time range
            cursor.execute(
                """
                SELECT SUM(cost / EXTRACT(EPOCH FROM (end_time - start_time)) * 3600) AS total_cost_hour
                FROM sub_project
                WHERE (start_time >= %s AND start_time < %s)
                OR (end_time > %s AND end_time <= %s)
                OR (start_time <= %s AND end_time >= %s);
                """,
                (start_of_hour, end_of_hour, start_of_hour, end_of_hour, start_of_hour, end_of_hour)
            )
            # Fetch and display the result for total cost per hour
            result_cost = cursor.fetchone()
            total_cost_hour = round(result_cost[0]) if result_cost else None
            if total_cost_hour is not None:
                print(f"Total cost per hour for sub-projects working from ({start_of_hour.strftime('%Y-%m-%d %H:%M:%S')}) to ({end_of_hour.strftime('%Y-%m-%d %H:%M:%S')}): {total_cost_hour}")
            else:
                print(f"No cost data available for the time range ({start_of_hour.strftime('%Y-%m-%d %H:%M:%S')}) to ({end_of_hour.strftime('%Y-%m-%d %H:%M:%S')}).")
            
            average_cost = total_cost_hour / count_sub_project
            person_loss = count_sub_project - max_person_count
            hourly_loss_calculation = round(average_cost * person_loss)
            print(f"Hourly loss calculation from ({start_of_hour.strftime('%Y-%m-%d %H:%M:%S')}) to ({end_of_hour.strftime('%Y-%m-%d %H:%M:%S')}): {hourly_loss_calculation}")
        else:
            total_cost_hour = 0
            hourly_loss_calculation = 0
            print("No loss calculation performed.")

        try:
            if start_of_hour.hour == 11 or start_of_hour.hour == 12:
                total_cost_hour = 0
                hourly_loss_calculation = 0
                
            # Insert data to database
            cursor.execute(
                """
                INSERT INTO hourly_loss (max_person, count_sub_project, total_cost, loss_calculation, calculate_time, project_id)
                VALUES (%s, %s, %s, %s, NOW(), 1);
                """,
                (max_person_count, count_sub_project, total_cost_hour, hourly_loss_calculation)
            )
            conn.commit()
            print(f"Data successfully inserted into hourly_loss table")
        except psycopg2.Error as e:
            print(f"Error inserting data into hourly_loss table: {e}")

except psycopg2.Error as e:
    print(f"Database error: {e}")

finally:
    # Close database connection
    cursor.close()
    conn.close()