import cv2
from ultralytics import YOLO
import psycopg2
from datetime import timedelta, datetime
import time
import os

# load input and model
try:
    # Load video from RTSP
    cctv_url = 'video-test/test1.mp4'
    if not cctv_url:
        raise ValueError("RTSP URL is not provided. Please provide a valid RTSP URL.")
    cap = cv2.VideoCapture(cctv_url)

    if not cap.isOpened():
        print("Error: Could not open video stream.")
        exit(1)

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30 

    frame_width = 1536
    frame_height = 864

    # Initialize variables
    frame_count = 0
    person_counts = []
    
    model = YOLO('yolov8l.pt')
    
    output_directory = 'video-playback/'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    current_time = time.strftime("%Y%m%d_%H%M%S")
    output_file_playback = os.path.join(output_directory, f"playback_{current_time}-1.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file_playback, fourcc, fps, (frame_width, frame_height))

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname='worker_detection',
        user='postgres',
        password='admin@123',
        host='localhost',
        port='5432'
    )
    cursor = conn.cursor()

    # Record the start time
    start_time = datetime.now()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            continue

        # Resize frame
        frame = cv2.resize(frame, (frame_width, frame_height))

        # Check elapsed time
        elapsed_time = time.time() - start_time.timestamp()
        if (elapsed_time >= 540) or cv2.waitKey(1) & 0xFF == ord('q'): 
            print("Time limit reached or 'q' key pressed. Stopping capture.")
            break

        frame_count += 1

        # Calculate timestamp
        seconds = frame_count / fps
        timestamp = str(timedelta(seconds=seconds)).split('.')[0] 

        # Detect objects and track objects
        results = model.track(frame, persist=True)

        # Filter out boxes that are not 'person' (assuming class 0 is 'person')
        person_boxes = [box for box in results[0].boxes if box.cls == 0]

        # Count persons
        person_count = len(person_boxes)
        person_counts.append(person_count)

        # Draw bounding boxes and annotations
        for box in person_boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
            person_id = int(box.id) if box.id is not None else 'N/A'
            confidence_score = float(box.conf)
            label = f"Person ID: {person_id}, Conf: {confidence_score:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

        # Draw the total person count in the top-left corner
        cv2.putText(frame, f'Total Persons: {person_count}', (10, 820),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
        
        # Calculate FPS
        current_fps = frame_count / (time.time() - start_time.timestamp())
        cv2.putText(frame, f'FPS: {current_fps:.2f}', (10, 850),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        # Write the frame with annotations to video file
        out.write(frame)

        # Filter Confidence
        rest_start_time = datetime.strptime("11:20", "%H:%M").time()
        rest_end_time = datetime.strptime("12:20", "%H:%M").time()

        if rest_start_time <= start_time.time() <= rest_end_time and confidence_score <= 50:
                person_count = 0
                print("Break time: Do Filter with Confidence below 50")

        # Write data to PostgreSQL database
        cursor.execute("""
        INSERT INTO person_counts (frame, timestamp, person_count)
        VALUES (%s, %s, %s)
        ON CONFLICT (frame, timestamp) DO NOTHING
        """, (frame_count, timestamp, person_count))
        conn.commit()
        
        # Display the frame with annotations
        # cv2.imshow('Frame', frame)

    # Record end time
    end_time = datetime.now()

    # Calculate and save max count that appears more than 15 times consecutively
    if person_counts:
        max_person_count = max(person_counts)

        if max_person_count is not None:
            cursor.execute("""
            INSERT INTO person_count_max (max_value, start_time, end_time, cctv_id)
            VALUES (%s, %s, %s, 1)
            """, (max_person_count, start_time, end_time))
            conn.commit()
            print(f"Maximum person count that appeared more than 15 times consecutively: {max_person_count}")
        else:
            print("No person count appeared more than 15 times consecutively.")

    # Close connection
    cursor.close()
    conn.close()
    cap.release()
    cv2.destroyAllWindows()

except Exception as e:
    # Log error message to the console
    print(f"Error occurred: {str(e)}")