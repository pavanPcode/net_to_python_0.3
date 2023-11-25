import cv2

stream_url = "http://192.168.1.3:5001"  # Replace with your stream URL
cap = cv2.VideoCapture(stream_url)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error reading frame from the video stream.")
        break

    cv2.imshow("Video Stream", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
