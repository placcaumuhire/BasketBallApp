import os
import sys
import time
from glob import glob
from datetime import datetime
from twelvelabs import TwelveLabs
from twelvelabs.models.task import Task
from twelvelabs.exceptions import BadRequestError

# Initialize TwelveLabs client with your API key
client = TwelveLabs(api_key=os.getenv('TL_API_KEY'))

# Create a function to dynamically select a video from the 'dataset' folder
def select_video():
    video_files = glob("dataset/*.mp4")
    if not video_files:
        print("No video files found in the 'dataset' folder.")
        return None
    print("Available videos:")
    for i, video_file in enumerate(video_files, 1):
        print(f"{i}. {os.path.basename(video_file)}")
    choice = input("Enter the number of the video you want to analyze: ")
    try:
        choice = int(choice)
        if 1 <= choice <= len(video_files):
            return video_files[choice - 1]
        else:
            print("Invalid choice. Please enter a number within the range.")
            return None
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return None

# Select the video to analyze
video_path = select_video()
if not video_path:
    exit()

# Create a unique index name based on current timestamp
index_name = f"index_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# Create the index with the dynamically generated name
index = client.index.create(
    name=index_name,
    engines=[
        {
            "name": "pegasus1",
            "options": ["visual", "conversation"],
        }
    ]
)
print(f"Index '{index_name}' created successfully.")

# Define a simple loading animation
def loading_animation():
    animation = "|/-\\"
    for i in range(20):
        sys.stdout.write("\r" + "Processing " + animation[i % len(animation)] + " ")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r")
    sys.stdout.flush()

# Upload the selected video
print("Uploading video...")
loading_animation()
task = client.task.create(index_id=index.id, file=video_path, language="en")
print("\nVideo uploaded successfully.")

# Monitor the video indexing process
print("Processing video...")
while True:
    loading_animation()
    try:
        task = client.task._get(task.id)  # Corrected the method name to _get
        if task.status == "ready":
            break
    except Exception as e:
        print(f"\nAn error occurred while retrieving task status: {e}")
        break
print("\nVideo processing completed.")

# Generate text from video
retry_count = 0
max_retries = 5
while retry_count < max_retries:
    try:
        res = client.generate.text(video_id=task.video_id, prompt="Analyze a basketball game video: track players and ball, shots made/missed, passing, player performance, defense, game flow, reactions, crowd, and broadcast data for insights into strategies and outcomes.")
        print(f"Comprehensive Analysis: {res.data}")
        break
    except BadRequestError as e:
        if "A video is not ready for generation" in str(e):
            print("Video not ready for text generation. Retrying...")
            retry_count += 1
            time.sleep(10)  # Wait for 10 seconds before retrying
        else:
            print("An unexpected error occurred. Exiting.")
            exit()

if retry_count == max_retries:
    print("Reached maximum retry attempts. Please try again later.")

# Close the loop for video processing
print("Video analysis completed.")
