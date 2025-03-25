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
    today = datetime.now().today
    start_of_hour = datetime.now()
    end_of_hour = start_of_hour + timedelta(hours=1)
    
    print(f"Analysis at ({start_of_hour.strftime('%Y-%m-%d %H:%M:%S')}) to ({end_of_hour.strftime('%Y-%m-%d %H:%M:%S')})")

    # Query to fetch the maximum `max_person_count` within the hour range
    cursor.execute(
        """
        SELECT MAX(max_value) AS max_person_count
        FROM person_count_max
        WHERE ((start_time >= %s AND start_time < %s)
            AND (end_time > %s AND end_time <= %s))
            and cctv_id = 1;
        """,
        (start_of_hour, end_of_hour, start_of_hour, end_of_hour)
    )
    result = cursor.fetchone()
    max_person_count = result[0] if result else 0
    if max_person_count is not None:
        print(f"Maximum person count based on detection: {max_person_count}")
    else:
        max_person_count = 0
        print("No data available.")

    # Query to fetch the count of time_sheet within the same hour range
    cursor.execute(
        """
        SELECT COUNT(DISTINCT t.employee_id) AS worker_count 
        FROM time_sheet t
        inner join work_center wc on wc.id = t.work_center_id
        inner join cctv c on c.work_center_id = wc.id 
        WHERE 
            ((t.start_time >= %s AND t.start_time < %s)
            OR (t.end_time > %s AND t.end_time <= %s)
            OR (t.start_time <= %s AND t.end_time >= %s))
            and c.id = 1;
        """,
        (start_of_hour, end_of_hour, start_of_hour, end_of_hour, start_of_hour, end_of_hour)
    )
    result_worksheet = cursor.fetchone()
    worker_count = result_worksheet[0] if result_worksheet else 0
    if worker_count:
        print(f"Worker count based on timesheet: {worker_count}")
    else:
        worker_count = 0
        print("No worker data available.")

    # Calculate hour_intime, hour_overtime, and hour_loss
    hour_intime = 0
    hour_overtime = 0
    hour_loss = 0

    if max_person_count is not None:
        # Execute the query once to get total cost per hour
        cursor.execute(
            """
            SELECT SUM(cost_per_hour) AS total_cost_per_hours
            FROM time_sheet t
            inner join work_center wc on wc.id = t.work_center_id
            inner join cctv c on c.work_center_id = wc.id 
            WHERE 
                ((t.start_time >= %s AND t.start_time < %s)
                OR (t.end_time > %s AND t.end_time <= %s)
                OR (t.start_time <= %s AND t.end_time >= %s))
                and c.id = 1;
            """,
            (start_of_hour, end_of_hour, start_of_hour, end_of_hour, start_of_hour, end_of_hour)
        )
        result_total_cost = cursor.fetchone()
        total_cost = result_total_cost[0] if result_total_cost else 0
        
        # Execute the query once to get plan hour
        cursor.execute(
            """
            SELECT plan_hour
            FROM project p
            inner join work_center wc on wc.project_id = p.id 
            inner join cctv c on c.work_center_id = wc.id 
            where c.id = 1;
            """
        )
        result_plan_hour = cursor.fetchone()
        plan_hour = result_plan_hour[0] if result_plan_hour else 0
        
        # Execute the query once to get progress
        cursor.execute(
            """
            SELECT progress
            FROM project p
            inner join work_center wc on wc.project_id = p.id 
            inner join cctv c on c.work_center_id = wc.id 
            where c.id = 1;
            """
        )
        result_progress = cursor.fetchone()
        progress = result_progress[0] if result_progress else 0

        if total_cost > 0:
            average_cost = round(total_cost / worker_count, 2)
            expected_progress = progress + (round((worker_count / plan_hour) * 100, 2))
        
            if worker_count < max_person_count:
                print("\nOvertime calculation")
                print(f"Total cost per hour based on timesheet: {total_cost}")
                print(f"Average cost per hour based on timesheet: {average_cost}")
                hour_overtime = max_person_count - worker_count
                print(f"Hour overtime: {hour_overtime} hours")
                overtime_cost = average_cost * hour_overtime
                print(f"Hourly overtime calculation: +{overtime_cost}")
                
                print("\nProgress calculation")
                print(f"Expected progress: {expected_progress}%")
                improving_progress = round((hour_overtime / plan_hour) * 100, 2)
                print(f"Improving progress: +{improving_progress}%")
                total_progress = round(expected_progress + improving_progress, 2)
                print(f"Total progress: {total_progress}%")
                
                hour_intime = 0
                hour_loss = 0
                loss_cost = 0
            
            elif worker_count > max_person_count:
                print("\nLoss calculation")
                print(f"Total cost per hour based on timesheet: {total_cost}")
                print(f"Average cost per hour based on timesheet: {average_cost}")
                hour_loss = worker_count - max_person_count
                print(f"Hour loss: {hour_loss} hours")
                loss_cost = average_cost * hour_loss
                print(f"Hourly loss calculation: -{loss_cost}")
                
                print("\nProgress calculation")
                print(f"Expected progress: {expected_progress}%")
                declining_progress = round((hour_loss / plan_hour) * 100, 2)
                print(f"Declining progress: -{declining_progress}%")
                total_progress = round(expected_progress - declining_progress, 2)
                print(f"Total progress: {total_progress}%")
                
                hour_intime = 0
                hour_overtime = 0
                overtime_cost = 0
            
            else:
                hour_intime = worker_count
                print(f"Hour intime: {hour_intime} hours")
                
                print("\nProgress calculation")
                total_progress = expected_progress
                print(f"Total progress: {total_progress}%")
                
                hour_loss = 0
                hour_overtime = 0
                overtime_cost = 0
                loss_cost = 0
            
            try:
                if start_of_hour.hour == 11:
                    max_person_count = 0
                    worker_count = 0
                    hour_intime = 0
                    hour_loss = 0
                    hour_overtime = 0
                    overtime_cost = 0
                    loss_cost = 0
                    expected_progress = 0
                    total_progress = 0
                    
                # Insert data to database
                cursor.execute(
                    """
                    INSERT INTO loss_analysis (detection_count, timesheet_count, hour_intime, hour_overtime, hour_loss, hour_overtime_calc, hour_loss_calc, expected_progress, total_progress, calculate_time, cctv_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1);
                    """,
                    (max_person_count, worker_count, hour_intime, hour_overtime, hour_loss, overtime_cost, loss_cost, expected_progress, total_progress, start_of_hour)
                )
                conn.commit()
                
                # Update data project
                cursor.execute(
                    """
                    UPDATE project p
                    SET progress = %s
                    FROM work_center wc
                    JOIN cctv c ON c.work_center_id = wc.id
                    WHERE wc.project_id = p.id AND c.id = 1;
                    """,
                    (total_progress,)
                )
                conn.commit()
                print("\nData successfully inserted into loss_analysis table")
            except psycopg2.Error as e:
                print(f"\nError inserting data into loss_analysis table: {e}")
    else:
        print("No data available.")

except psycopg2.Error as e:
    print(f"Database error: {e}")

finally:
    # Close database connection
    cursor.close()
    conn.close()
