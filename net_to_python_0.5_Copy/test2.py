import tkinter as tk
import cv2
from PIL import Image, ImageTk
import requests
import numpy as np

#pip install opencv-python Pillow


def fetch_and_display_stream(url):
    # Open the video stream
    cap = cv2.VideoCapture(url)
    # Check if the stream is opened successfully
    if not cap.isOpened():
        text.insert(tk.END, "Failed to open the stream.")
        return

    # Function to update the video frame
    def update_frame():
        ret, frame = cap.read()
        if ret:
            # Convert the frame to RGB format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to PIL Image
            image = Image.fromarray(frame_rgb)

            # Convert PIL Image to PhotoImage
            photo = ImageTk.PhotoImage(image=image)

            # Update the label with the new frame
            label.config(image=photo)
            label.image = photo
            label.after(10, update_frame)  # Repeat after 10 milliseconds
        else:
            text.insert(tk.END, "Failed to read frame.")
            cap.release()

    # Call the update_frame function to start displaying the stream
    update_frame()


# Create the main application window
app = tk.Tk()
app.title("Live Stream Viewer")

# Create a label to display the video stream
label = tk.Label(app)
label.pack()

# Create a text widget for messages
text = tk.Text(app, wrap=tk.WORD, width=40, height=5)
text.pack()

# Replace 'your_stream_url' with the desired stream URL
stream_url = 'http://192.168.1.3:5001/'

# Fetch and display the live stream
fetch_and_display_stream(stream_url)

# Start the application event loop
app.mainloop()
