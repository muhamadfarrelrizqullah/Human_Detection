import subprocess
import cv2
from ultralytics import YOLO
import psycopg2
from datetime import timedelta, datetime
import time
import os
import csv
import paramiko

# Download video function
def download_playback_video(input_file, output_file, duration):
    try:
        ffmpeg_command = [
            "ffmpeg", "-i", input_file, "-t", duration, "-c:v", "libx264", "-crf", "23", "-preset", "fast", "-c:a", "aac", output_file
        ]
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error in downloading playback video: {e}")

# Delete video function
def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File {file_path} has been deleted.")
        else:
            print(f"File {file_path} not found.")
    except OSError as e:
        print(f"Error deleting file {file_path}: {e}")

# Upload video function
def upload_file_to_server(local_file_path, remote_file_path):
    try:
        if not os.path.exists(local_file_path):
            raise FileNotFoundError(f"File {local_file_path} not found")

        ssh_host = 'localhost'
        ssh_port = 22
        ssh_user = 'user'
        ssh_password = 'pw'

        transport = paramiko.Transport((ssh_host, ssh_port))
        transport.connect(username=ssh_user, password=ssh_password)

        sftp = paramiko.SFTPClient.from_transport(transport)

        remote_directory = os.path.dirname(remote_file_path)
        try:
            sftp.stat(remote_directory)
        except FileNotFoundError:
            print(f"Create directory remote : {remote_directory}")
            sftp.mkdir(remote_directory)

        print(f"Upload {local_file_path} to {remote_file_path}...")
        sftp.put(local_file_path, remote_file_path)
        print(f"File {local_file_path} has been uploaded at {remote_file_path}")

        sftp.close()
        transport.close()
    except FileNotFoundError as e:
        print(f"Error uploading file to server: {e}")
    except paramiko.SSHException as e:
        print(f"Error connection SSH: {e}")
    except Exception as e:
        print(f"Error uploading file to server: {e}")

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

    # Close video writer
    out.release()

    # Record end time
    end_time = datetime.now()

    # Download the annotated video (1 minute clip from the recorded 10 minutes video)
    download_duration = "00:01:00"
    output_file_download = os.path.join(output_directory, f"download_{current_time}-1.mp4")
    download_playback_video(output_file_playback, output_file_download, download_duration)

    # Calculate and save max count that appears more than 15 times consecutively
    if person_counts:
        max_person_count = None
        consecutive_count = 1

        for i in range(1, len(person_counts)):
            if person_counts[i] == person_counts[i - 1]:
                consecutive_count += 1
            else:
                consecutive_count = 1

            if consecutive_count > 15:
                if max_person_count is None or person_counts[i] > max_person_count:
                    max_person_count = person_counts[i]

        if max_person_count is not None:
            video_filename = os.path.basename(output_file_download)
            relative_video_path = f"playback/{video_filename}"

            cursor.execute("""
            INSERT INTO job (job_message, created_at)
            VALUES (%s, %s)
            RETURNING id
            """, (f"Success detect {max_person_count} at {end_time}", end_time))

            successjob_id = cursor.fetchone()[0]
            conn.commit()

            cursor.execute("""
            INSERT INTO person_count_max (max_value, start_time, end_time, video_path, job_id, cctv_id)
            VALUES (%s, %s, %s, %s, %s, 1)
            """, (max_person_count, start_time, end_time, relative_video_path, successjob_id))
            conn.commit()
            print(f"Maximum person count that appeared more than 15 times consecutively: {max_person_count}")
        else:
            print("No person count appeared more than 15 times consecutively.")

    # Upload file to server
    upload_file_to_server(output_file_download, 'Videos/playback/download_{}-1.mp4'.format(current_time))

    # Delete file after upload
    delete_file(output_file_playback)
    delete_file(output_file_download)

    # Close connection
    cursor.close()
    conn.close()
    cap.release()
    cv2.destroyAllWindows()

except Exception as e:
    # Log error message to the console
    print(f"Error occurred: {str(e)}")