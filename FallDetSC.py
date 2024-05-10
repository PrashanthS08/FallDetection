import cv2
import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

def show_alert():
    # Function to show the alert pop-up
    print("Fall detected for more than 2 seconds!")
    # Implement your alert pop-up here (e.g., using GUI libraries like Tkinter)

def send_email_alert(subject, body, to, frame):
    # Function to send an email alert with the attached photo frame
    msg = MIMEMultipart()
    msg.attach(MIMEText(body, 'plain'))
    msg['subject'] = subject
    msg['to'] = to

    user = "prashuprashanth988@gmail.com"
    msg['from'] = user
    password = "lbkmxyamghmhnbfb"  

    try:
        # Convert the frame to a bytes buffer
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Attach the frame as an image to the email
        image = MIMEImage(frame_bytes, name='frame.jpg')
        msg.attach(image)

        # Send the email
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
        print("Email alert sent successfully!")
        server.quit()
    except Exception as e:
        print("Error sending email alert:", str(e))

def fall_timer():
    # Function to handle fall duration timing
    global fall_start_time, fall_detected

    while True:
        if fall_detected:
            current_time = time.time()
            fall_duration = current_time - fall_start_time

            if fall_duration >= 2:
                # Show alert pop-up when the fall is detected for more than 2 seconds
                show_alert()
                # Send an email alert with the frame attached
                send_email_alert("Fall Detected!", "Fall detected for more than 2 seconds!", "gsdanawadkar5@gmail.com", frame)

            time.sleep(1)  # Check every half second

fitToEllipse = False
cap = cv2.VideoCapture('C:/Users/VTU/OneDrive/Desktop/FallDetection/Test1.mp4')
time.sleep(2)

fgbg = cv2.createBackgroundSubtractorMOG2()
j = 0

fall_detected = False
fall_start_time = 0

# Create and start the fall duration timing thread
fall_timer_thread = threading.Thread(target=fall_timer)
fall_timer_thread.daemon = True
fall_timer_thread.start()

while True:
    ret, frame = cap.read()

    if not ret:
        break

    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fgmask = fgbg.apply(gray)

        contours, _ = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            areas = [cv2.contourArea(contour) for contour in contours]
            max_area = max(areas, default=0)
            max_area_index = areas.index(max_area)
            cnt = contours[max_area_index]
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.drawContours(fgmask, [cnt], 0, (255, 255, 255), 3, maxLevel=0)

            if h < w:
                j += 1

            if j > 10 and not fall_detected:
                fall_detected = True
                fall_start_time = time.time()

            if h > w:
                j = 0
                if fall_detected:
                    fall_detected = False

            # Draw the bounding rectangle with the "Fall Detected" tag if a fall is detected
            color = (0, 0, 255) if fall_detected else (0, 255, 0)
            tag = "Fall Detected" if fall_detected else ""
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, tag, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv2.imshow('video', frame)

        if cv2.waitKey(33) == 27:
            break
    except Exception as e:
        break

cv2.destroyAllWindows()
cap.release()
