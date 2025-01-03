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
    start_of_hour = today.replace(hour=9, minute=30, second=0, microsecond=0)
    end_of_hour = start_of_hour + timedelta(hours=1)
    
    print(f"Analysis at ({start_of_hour.strftime('%Y-%m-%d %H:%M:%S')}) to ({end_of_hour.strftime('%Y-%m-%d %H:%M:%S')})")

    # Query to fetch the maximum `max_person_count` within the hour range
    cursor.execute(
        """
        SELECT MAX(max_value) AS max_person_count
        FROM person_count_max
        WHERE (start_time >= %s AND start_time < %s)
        OR (end_time > %s AND end_time <= %s)
        OR (start_time <= %s AND end_time >= %s);
        """,
        (start_of_hour, end_of_hour, start_of_hour, end_of_hour, start_of_hour, end_of_hour)
    )
    result = cursor.fetchone()
    max_person_count = result[0] if result else 0
    if max_person_count is not None:
        print(f"Maximum person count based on detection: {max_person_count}")
    else:
        print(f"No data available.")

    # Query to fetch the count of time_sheet within the same hour range
    cursor.execute(
        """
        SELECT COUNT(DISTINCT employee_id) AS worker_count 
        FROM time_sheet
        WHERE (start_time >= %s AND start_time < %s)
        OR (end_time > %s AND end_time <= %s)
        OR (start_time <= %s AND end_time >= %s);
        """,
        (start_of_hour, end_of_hour, start_of_hour, end_of_hour, start_of_hour, end_of_hour)
    )
    result_worksheet = cursor.fetchone()
    worker_count = result_worksheet[0] if result_worksheet else 0
    if worker_count:
        print(f"Worker count based on timesheet: {worker_count}")
    else:
        print(f"No worker data available.")

    # Calculate hour_intime, hour_overtime, and hour_loss
    hour_intime = 0
    hour_overtime = 0
    hour_loss = 0

    if max_person_count is not None:
        # Execute the query once to get total cost per hour
        cursor.execute(
            """
            SELECT SUM(cost_per_hour) AS total_cost_per_hours
            FROM time_sheet
            WHERE (start_time >= %s AND start_time < %s)
            OR (end_time > %s AND end_time <= %s)
            OR (start_time <= %s AND end_time >= %s);
            """,
            (start_of_hour, end_of_hour, start_of_hour, end_of_hour, start_of_hour, end_of_hour)
        )
        result_total_cost = cursor.fetchone()
        total_cost = result_total_cost[0] if result_total_cost else 0
        
        # Execute the query once to get plan hour
        cursor.execute(
            """
            SELECT plan_hour
            FROM project
            WHERE id = 1;
            """
        )
        result_plan_hour = cursor.fetchone()
        plan_hour = result_plan_hour[0] if result_plan_hour else 0

        if total_cost > 0:
            average_cost = round(total_cost / worker_count, 2)
            expected_progress = (worker_count / plan_hour) * 100
        
            if worker_count < max_person_count:
                print("\nOvertime calculation")
                print(f"Total cost per hour based on timesheet: {total_cost}")
                print(f"Average cost per hour based on timesheet: {average_cost}")
                hour_overtime = max_person_count - worker_count
                print(f"Hour overtime: {hour_overtime} hours")
                hourly_overtime = average_cost * hour_overtime
                print(f"Hourly overtime calculation: +{hourly_overtime}")
                
                print("\nProgress calculation")
                print(f"Expected progress: {expected_progress}%")
                improving_progress = (hour_overtime / plan_hour) * 100
                print(f"Improving progress: +{improving_progress}%")
                total_progress = expected_progress + improving_progress
                print(f"Total progress: {total_progress}%")
            
            elif worker_count > max_person_count:
                print("\nLoss calculation")
                print(f"Total cost per hour based on timesheet: {total_cost}")
                print(f"Average cost per hour based on timesheet: {average_cost}")
                hour_loss = worker_count - max_person_count
                print(f"Hour loss: {hour_loss} hours")
                hourly_loss = average_cost * hour_loss
                print(f"Hourly loss calculation: -{hourly_loss}")
                
                print("\nProgress calculation")
                print(f"Expected progress: {expected_progress}%")
                declining_progress = (hour_loss / plan_hour) * 100
                print(f"Declining progress: -{declining_progress}%")
                total_progress = expected_progress - declining_progress
                print(f"Total progress: {total_progress}%")
            
            else:
                hour_intime = worker_count
                print(f"Hour intime: {hour_intime} hours")
    else:
        print("No total cost found for the specified time range.")


except psycopg2.Error as e:
    print(f"Database error: {e}")

finally:
    # Close database connection
    cursor.close()
    conn.close()
